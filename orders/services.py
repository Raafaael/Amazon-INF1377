"""Contratos de criação e evolução de pedidos para checkout, pagamento e entrega."""

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from addresses.models import Endereco
from cart.models import Carrinho

from .models import HistoricoStatusPedido, ItemPedido, Pedido


TRANSICOES = {
    Pedido.Status.AGUARDANDO_PAGAMENTO: {
        Pedido.Status.PAGAMENTO_APROVADO,
        Pedido.Status.PAGAMENTO_RECUSADO,
        Pedido.Status.CANCELADO,
    },
    Pedido.Status.PAGAMENTO_RECUSADO: {
        Pedido.Status.AGUARDANDO_PAGAMENTO,
        Pedido.Status.CANCELADO,
    },
    Pedido.Status.PAGAMENTO_APROVADO: {Pedido.Status.EM_PREPARACAO, Pedido.Status.CANCELADO},
    Pedido.Status.EM_PREPARACAO: {Pedido.Status.ENVIADO, Pedido.Status.CANCELADO},
    Pedido.Status.ENVIADO: {Pedido.Status.ENTREGUE},
    Pedido.Status.ENTREGUE: set(),
    Pedido.Status.CANCELADO: set(),
}


def _valor_monetario(valor, nome):
    if not isinstance(valor, Decimal) or not valor.is_finite():
        raise ValidationError(f'{nome} deve ser um valor Decimal válido.')
    try:
        if valor < 0 or valor != valor.quantize(Decimal('0.01')) or valor >= Decimal('10000000000'):
            raise ValidationError(f'{nome} deve ser não negativo e ter no máximo duas casas decimais.')
    except InvalidOperation as erro:
        raise ValidationError(f'{nome} deve ser um valor Decimal válido.') from erro
    return valor


@transaction.atomic
def criar_pedido(usuario, chave_checkout, *, endereco=None, frete=Decimal('0.00'),
                 tipo_entrega='', prazo_entrega_dias=None, previsao_entrega=None):
    """Congela o carrinho uma vez por (usuário, chave); não baixa nem limpa estoque.

    A chave é gerada pelo checkout para a intenção de compra, e reutilizada em
    reenvios. Em um reenvio, devolve o pedido original sem reler o carrinho.
    """
    if not usuario.is_authenticated:
        raise ValidationError('Entre para criar um pedido.')
    if not isinstance(chave_checkout, str) or not chave_checkout.strip() or len(chave_checkout) > 64:
        raise ValidationError('Informe uma chave de checkout válida (até 64 caracteres).')
    pedido_anterior = Pedido.objects.filter(usuario=usuario, chave_checkout=chave_checkout).first()
    if pedido_anterior:
        return pedido_anterior

    frete = _valor_monetario(frete, 'Frete')
    if tipo_entrega not in ('', *Pedido.TipoEntrega.values):
        raise ValidationError('Modalidade de entrega inválida.')
    if (frete or prazo_entrega_dias is not None or previsao_entrega) and not tipo_entrega:
        raise ValidationError('Informe a modalidade para registrar frete ou prazo.')
    if prazo_entrega_dias is not None and (not isinstance(prazo_entrega_dias, int) or isinstance(prazo_entrega_dias, bool) or prazo_entrega_dias < 0):
        raise ValidationError('O prazo deve ser um número de dias não negativo.')
    if endereco is not None:
        if not isinstance(endereco, Endereco) or endereco.usuario_id != usuario.pk or not Endereco.objects.filter(pk=endereco.pk, usuario=usuario).exists():
            raise ValidationError('Selecione um endereço pertencente ao cliente.')
    if tipo_entrega and endereco is None:
        raise ValidationError('Selecione um endereço para a entrega informada.')

    carrinho = Carrinho.objects.select_for_update().filter(usuario=usuario).first()
    itens = list(carrinho.itens.select_related('produto').select_for_update().order_by('pk')) if carrinho else []
    if not itens:
        raise ValidationError('O carrinho está vazio.')

    snapshots = []
    for item in itens:
        produto = item.produto
        if item.quantidade < 1 or item.quantidade > produto.estoque:
            raise ValidationError(f'Estoque insuficiente ou quantidade inválida para "{produto.nome}".')
        preco = _valor_monetario(produto.preco, 'Preço unitário')
        if preco <= 0:
            raise ValidationError('O preço unitário deve ser positivo.')
        snapshots.append((produto, produto.nome, item.quantidade, preco, preco * item.quantidade))

    subtotal = sum((valor for _, _, _, _, valor in snapshots), Decimal('0.00'))
    total = subtotal + frete
    _valor_monetario(subtotal, 'Subtotal')
    _valor_monetario(total, 'Total')
    pedido = Pedido.objects.create(
        usuario=usuario, chave_checkout=chave_checkout,
        subtotal_itens=subtotal, frete=frete, total=total,
        tipo_entrega=tipo_entrega,
        endereco_entrega=endereco.texto_formatado if endereco else '',
        endereco_dados=endereco.dados_para_pedido() if endereco else {},
        prazo_entrega_dias=prazo_entrega_dias, previsao_entrega=previsao_entrega,
    )
    ItemPedido.objects.bulk_create([
        ItemPedido(pedido=pedido, produto=produto, nome_produto=nome,
                   quantidade=quantidade, preco_unitario=preco, subtotal=subtotal_item)
        for produto, nome, quantidade, preco, subtotal_item in snapshots
    ])
    HistoricoStatusPedido.objects.create(pedido=pedido, status=pedido.status,
                                        observacao='Pedido criado; aguardando pagamento simulado.')
    return pedido


@transaction.atomic
def atualizar_status(pedido, novo_status, *, origem, usuario=None, observacao=''):
    """Altera status em transação e registra o evento; chamar apenas de fluxo confiável.

    origem='pagamento' é usada pelo módulo de pagamento após resultado simulado;
    origem='entrega' pelo módulo de entrega; origem='administracao' exige staff.
    Nenhuma view de cliente chama esta função diretamente.
    """
    if origem not in ('pagamento', 'entrega', 'administracao'):
        raise ValidationError('Origem da alteração inválida.')
    if origem == 'administracao' and (usuario is None or not usuario.is_authenticated or not usuario.is_staff):
        raise ValidationError('Somente a administração pode executar esta ação.')
    pedido_atual = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if novo_status not in TRANSICOES.get(pedido_atual.status, set()):
        raise ValidationError('Transição de status não permitida.')
    if origem == 'pagamento' and novo_status not in (Pedido.Status.PAGAMENTO_APROVADO, Pedido.Status.PAGAMENTO_RECUSADO, Pedido.Status.AGUARDANDO_PAGAMENTO):
        raise ValidationError('O pagamento só pode registrar seu próprio resultado.')
    if origem == 'entrega' and novo_status not in (Pedido.Status.EM_PREPARACAO, Pedido.Status.ENVIADO, Pedido.Status.ENTREGUE):
        raise ValidationError('A entrega só pode avançar seus estados.')
    if origem == 'administracao' and novo_status in (Pedido.Status.PAGAMENTO_APROVADO, Pedido.Status.PAGAMENTO_RECUSADO, Pedido.Status.AGUARDANDO_PAGAMENTO):
        raise ValidationError('O resultado de pagamento exige o simulador.')
    if len(observacao) > 255:
        raise ValidationError('A observação deve ter até 255 caracteres.')

    pedido_atual.status = novo_status
    campos = ['status']
    agora = timezone.now()
    if novo_status == Pedido.Status.ENVIADO:
        pedido_atual.enviado_em = agora
        campos.append('enviado_em')
    if novo_status == Pedido.Status.ENTREGUE:
        if pedido_atual.enviado_em is None:
            raise ValidationError('O pedido precisa ter sido enviado antes da entrega.')
        pedido_atual.entregue_em = agora
        campos.append('entregue_em')
    pedido_atual.save(update_fields=campos)
    HistoricoStatusPedido.objects.create(pedido=pedido_atual, status=novo_status,
                                        observacao=observacao)
    return pedido_atual
