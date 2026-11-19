"""Simulador de pagamentos (cartão fictício e PIX de demonstração).

Nenhuma função aqui contata banco ou gateway. O status do pedido só muda pelo
contrato `orders.services.atualizar_status(..., origem='pagamento')`.
"""

import re
import secrets
import uuid
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Pedido
from orders.services import atualizar_status

from .models import MAX_PARCELAS, Pagamento, PagamentoCartao, PagamentoPix

EXPIRACAO_PIX = timedelta(minutes=1)
MENSAGEM_PIX_EXPIRADO = 'PIX simulado expirado.'
STATUS_PAGAVEIS = (Pedido.Status.AGUARDANDO_PAGAMENTO, Pedido.Status.PAGAMENTO_RECUSADO)


# ---------------------------------------------------------------- validações


def somente_digitos(valor):
    return re.sub(r'\D', '', valor or '')


def luhn_valido(numero):
    soma = 0
    for i, d in enumerate(reversed(numero)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        soma += n
    return soma % 10 == 0


def validar_numero_cartao(numero):
    digitos = somente_digitos(numero)
    if len(digitos) != 16:
        raise ValidationError('O número do cartão deve ter 16 dígitos.')
    if not luhn_valido(digitos):
        raise ValidationError('Número de cartão inválido.')
    return digitos


def validar_validade(validade, hoje=None):
    """Formato MM/AA; aceita até o último dia do mês informado."""
    m = re.fullmatch(r'(\d{2})/(\d{2})', (validade or '').strip())
    if not m:
        raise ValidationError('Informe a validade no formato MM/AA.')
    mes, ano = int(m.group(1)), 2000 + int(m.group(2))
    if not 1 <= mes <= 12:
        raise ValidationError('Mês de validade inválido.')
    hoje = hoje or timezone.localdate()
    if (ano, mes) < (hoje.year, hoje.month):
        raise ValidationError('Cartão vencido.')
    return mes, ano


def validar_cvv(cvv):
    if not re.fullmatch(r'\d{3}', (cvv or '').strip()):
        raise ValidationError('O CVV deve ter 3 dígitos.')


def validar_nome(nome):
    nome = ' '.join((nome or '').split())
    if len(nome) < 3 or not re.fullmatch(r"[A-Za-zÀ-ÿ' ]+", nome):
        raise ValidationError('Informe o nome impresso no cartão (somente letras).')
    return nome


def validar_parcelas(parcelas):
    if isinstance(parcelas, bool) or not isinstance(parcelas, int) or not 1 <= parcelas <= MAX_PARCELAS:
        raise ValidationError(f'Escolha entre 1 e {MAX_PARCELAS} parcelas.')
    return parcelas


def valor_parcela(total, parcelas):
    return (total / parcelas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def bandeira_ficticia(numero):
    if numero.startswith('4'):
        return 'Visa (teste)'
    if numero[:2] in {'51', '52', '53', '54', '55'}:
        return 'Mastercard (teste)'
    return 'Cartão de teste'


def _autorizacao_simulada():
    """Sorteia uma aprovação ou recusa, com a mesma chance para cada resultado."""
    return secrets.randbelow(2) == 1


# ---------------------------------------------------------------- apoio


def _pedido_pagavel(usuario, pedido):
    """Bloqueia o pedido e garante que é do usuário e ainda aceita pagamento."""
    if not usuario.is_authenticated:
        raise ValidationError('Entre para pagar.')
    atual = Pedido.objects.select_for_update().filter(pk=pedido.pk, usuario=usuario).first()
    if atual is None:
        raise ValidationError('Pedido não encontrado.')
    if atual.status not in STATUS_PAGAVEIS:
        raise ValidationError('Este pedido não aceita novo pagamento.')
    return atual


def _reabrir_se_recusado(pedido):
    if pedido.status == Pedido.Status.PAGAMENTO_RECUSADO:
        pedido = atualizar_status(pedido, Pedido.Status.AGUARDANDO_PAGAMENTO, origem='pagamento',
                                  observacao='Nova tentativa de pagamento simulado.')
    return pedido


def expirar_pix_vencidos(pedido):
    """Marca como cancelados os PIX pendentes cuja validade terminou."""
    return (Pagamento.objects
            .filter(pedido=pedido, modalidade=Pagamento.Modalidade.PIX, status=Pagamento.Status.PENDENTE,
                    pix__expira_em__lte=timezone.now())
            .update(status=Pagamento.Status.CANCELADO, mensagem=MENSAGEM_PIX_EXPIRADO,
                    atualizado_em=timezone.now()))


def ultimo_pix_expirou(pedido):
    """True quando a tentativa mais recente do pedido é um PIX que expirou."""
    ultima = Pagamento.objects.filter(pedido=pedido).order_by('-criado_em', '-id').first()
    return bool(ultima and ultima.modalidade == Pagamento.Modalidade.PIX
                and ultima.status == Pagamento.Status.CANCELADO
                and ultima.mensagem == MENSAGEM_PIX_EXPIRADO)


def pix_ativo(pedido):
    expirar_pix_vencidos(pedido)
    return (Pagamento.objects.select_related('pix')
            .filter(pedido=pedido, modalidade=Pagamento.Modalidade.PIX, status=Pagamento.Status.PENDENTE)
            .first())


# ---------------------------------------------------------------- cartão


@transaction.atomic
def pagar_com_cartao(usuario, pedido, *, numero, nome, validade, cvv, parcelas=1):
    """Valida os dados fictícios, registra o resultado e atualiza o pedido.

    O CVV, o nome e a validade são apenas validados; nada disso é persistido.
    Devolve o `Pagamento` (APROVADO ou RECUSADO).
    """
    pedido = _pedido_pagavel(usuario, pedido)
    digitos = validar_numero_cartao(numero)
    validar_nome(nome)
    validar_validade(validade)
    validar_cvv(cvv)
    parcelas = validar_parcelas(parcelas)

    # Um PIX em aberto deixa de valer quando o cliente opta pelo cartão.
    Pagamento.objects.filter(pedido=pedido, modalidade=Pagamento.Modalidade.PIX,
                             status=Pagamento.Status.PENDENTE).update(
        status=Pagamento.Status.CANCELADO, mensagem='Substituído por pagamento com cartão.',
        atualizado_em=timezone.now())
    pedido = _reabrir_se_recusado(pedido)

    aprovado = _autorizacao_simulada()
    status = Pagamento.Status.APROVADO if aprovado else Pagamento.Status.RECUSADO
    mensagem = ('Pagamento aprovado pela operadora simulada.' if aprovado else
                'Dados do cartão válidos, mas o pagamento foi recusado pela operadora simulada. '
                'Tente outro cartão ou pague com PIX.')
    pagamento = Pagamento.objects.create(pedido=pedido, modalidade=Pagamento.Modalidade.CARTAO,
                                         valor=pedido.total, status=status, mensagem=mensagem)
    PagamentoCartao.objects.create(pagamento=pagamento, bandeira=bandeira_ficticia(digitos),
                                   ultimos_digitos=digitos[-4:], parcelas=parcelas,
                                   valor_parcela=valor_parcela(pedido.total, parcelas))
    novo_status = Pedido.Status.PAGAMENTO_APROVADO if aprovado else Pedido.Status.PAGAMENTO_RECUSADO
    atualizar_status(pedido, novo_status, origem='pagamento',
                     observacao=f'Cartão fictício final {digitos[-4:]} ({parcelas}x): '
                                f'{"aprovado" if aprovado else "recusado"} na simulação.')
    return pagamento


# ---------------------------------------------------------------- PIX


@transaction.atomic
def gerar_pix(usuario, pedido):
    """Gera (ou reaproveita, se ainda válido) um PIX simulado PENDENTE.

    Gerar o QR não confirma nada: o pedido continua aguardando pagamento.
    """
    pedido = _pedido_pagavel(usuario, pedido)
    existente = pix_ativo(pedido)
    if existente:
        return existente
    pedido = _reabrir_se_recusado(pedido)
    pagamento = Pagamento.objects.create(
        pedido=pedido, modalidade=Pagamento.Modalidade.PIX, valor=pedido.total,
        mensagem='Aguardando confirmação do PIX simulado.')
    PagamentoPix.objects.create(pagamento=pagamento,
                                codigo=f'PIXSIM-{uuid.uuid4().hex[:20].upper()}',
                                expira_em=timezone.now() + EXPIRACAO_PIX)
    return pagamento


def _pix_do_usuario(usuario, pagamento):
    if not usuario.is_authenticated:
        raise ValidationError('Entre para continuar.')
    atual = (Pagamento.objects.select_for_update().select_related('pix')
             .filter(pk=pagamento.pk, pedido__usuario=usuario, modalidade=Pagamento.Modalidade.PIX)
             .first())
    if atual is None:
        raise ValidationError('PIX não encontrado.')
    if atual.status != Pagamento.Status.PENDENTE:
        raise ValidationError('Este PIX não está mais pendente.')
    return atual


@transaction.atomic
def confirmar_pix(usuario, pagamento):
    """Ação explícita “Simular pagamento PIX”: aprova o PIX e marca o pedido como pago."""
    pagamento = _pix_do_usuario(usuario, pagamento)
    pedido = Pedido.objects.select_for_update().get(pk=pagamento.pedido_id)
    if pagamento.pix.expirado:
        # A transação é desfeita pela exceção; expirar_pix_vencidos() o cancela depois.
        raise ValidationError('Este PIX expirou. Gere um novo código.')
    if pedido.status != Pedido.Status.AGUARDANDO_PAGAMENTO or pagamento.valor != pedido.total:
        raise ValidationError('O pedido não está aguardando este pagamento.')
    pagamento.status = Pagamento.Status.APROVADO
    pagamento.mensagem = 'PIX simulado confirmado.'
    pagamento.save(update_fields=['status', 'mensagem', 'atualizado_em'])
    atualizar_status(pedido, Pedido.Status.PAGAMENTO_APROVADO, origem='pagamento',
                     observacao=f'PIX simulado {pagamento.pix.codigo} confirmado.')
    return pagamento


@transaction.atomic
def cancelar_pix(usuario, pagamento):
    """Cancela um PIX pendente; o pedido continua aguardando pagamento."""
    pagamento = _pix_do_usuario(usuario, pagamento)
    pagamento.status = Pagamento.Status.CANCELADO
    pagamento.mensagem = 'PIX simulado cancelado pelo cliente.'
    pagamento.save(update_fields=['status', 'mensagem', 'atualizado_em'])
    return pagamento
