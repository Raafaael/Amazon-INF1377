"""Composição dos contratos da Semana 2, sem duplicar seus simuladores."""

from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from addresses.models import Endereco
from cart.models import Carrinho
from catalog.models import Produto
from orders import services as pedidos
from orders.models import Pedido
from payments import services as pagamentos
from payments.models import Pagamento
from shipping import services as entregas

from .models import Checkout


def resumo_carrinho(usuario):
    carrinho = Carrinho.objects.filter(usuario=usuario).first()
    itens = list(carrinho.itens_com_produto()) if carrinho else []
    if not itens:
        raise ValidationError('O carrinho está vazio. Adicione produtos para finalizar a compra.')
    for item in itens:
        if item.quantidade < 1 or item.quantidade > item.produto.estoque:
            raise ValidationError(f'Estoque insuficiente para "{item.produto.nome}". Revise o carrinho.')
        if not item.produto.preco.is_finite() or item.produto.preco <= 0:
            raise ValidationError('Há um produto com preço inválido. Revise o carrinho.')
    return [
        {'item_id': item.pk, 'produto_id': item.produto_id, 'nome': item.produto.nome,
         'quantidade': item.quantidade, 'preco': str(item.produto.preco),
         'subtotal': str(item.subtotal)}
        for item in itens
    ]


@transaction.atomic
def iniciar(usuario, checkout_id=None):
    resumo = resumo_carrinho(usuario)
    atual = Checkout.objects.filter(pk=checkout_id, usuario=usuario).first() if checkout_id else None
    if atual and not atual.estoque_baixado and atual.resumo_carrinho == resumo:
        return atual
    return Checkout.objects.create(usuario=usuario, resumo_carrinho=resumo)


def validar_carrinho(checkout):
    if resumo_carrinho(checkout.usuario) != checkout.resumo_carrinho:
        raise ValidationError('O carrinho ou o preço de um produto mudou. Volte ao carrinho e inicie novamente para revisar os valores.')


@transaction.atomic
def selecionar_endereco(checkout, endereco):
    checkout = Checkout.objects.select_for_update().get(pk=checkout.pk)
    if checkout.pedido_id:
        return checkout
    validar_carrinho(checkout)
    endereco = Endereco.obter_do_usuario(checkout.usuario, endereco.pk)
    dados = endereco.dados_para_pedido()
    # Voltar uma etapa sem alterar o endereço preserva a mesma cotação.
    if checkout.endereco_dados != dados or not checkout.cotacoes:
        checkout.cotacoes = {}
        for tipo in ('PADRAO', 'EXPRESSA'):
            cotacao = entregas.cotar_frete(endereco.cep, tipo)
            checkout.cotacoes[tipo] = {
                'valor': str(cotacao['valor']), 'prazo_dias': cotacao['prazo_dias'],
                'tipo': cotacao['tipo'], 'previsao': cotacao['previsao'].isoformat(),
            }
        checkout.modalidade = ''
    checkout.endereco = endereco
    checkout.endereco_dados = dados
    checkout.save(update_fields=['endereco', 'endereco_dados', 'cotacoes', 'modalidade'])
    return checkout


@transaction.atomic
def selecionar_entrega(checkout, modalidade):
    checkout = Checkout.objects.select_for_update().get(pk=checkout.pk)
    if checkout.pedido_id:
        return checkout
    validar_carrinho(checkout)
    validar_endereco(checkout)
    if modalidade not in checkout.cotacoes:
        raise ValidationError('Selecione uma das modalidades cotadas.')
    checkout.modalidade = modalidade
    checkout.save(update_fields=['modalidade'])
    return checkout


def validar_endereco(checkout):
    endereco = Endereco.objects.filter(pk=checkout.endereco_id, usuario=checkout.usuario).first()
    if not endereco or endereco.dados_para_pedido() != checkout.endereco_dados:
        raise ValidationError('O endereço mudou ou não está mais disponível. Selecione o endereço novamente.')
    return endereco


@transaction.atomic
def confirmar_pedido(checkout):
    checkout = Checkout.objects.select_for_update().get(pk=checkout.pk)
    if checkout.pedido_id:
        return checkout.pedido
    # Impede mudanças durante o congelamento dos itens pelo serviço de Breno.
    carrinho = Carrinho.objects.select_for_update().filter(usuario=checkout.usuario).first()
    if carrinho:
        list(carrinho.itens.select_for_update())
    list(Produto.objects.select_for_update().filter(
        pk__in=[item['produto_id'] for item in checkout.resumo_carrinho]).order_by('pk'))
    validar_carrinho(checkout)
    endereco = validar_endereco(checkout)
    cotacao = checkout.cotacoes.get(checkout.modalidade)
    if not cotacao:
        raise ValidationError('Selecione a modalidade de entrega antes de confirmar.')
    pedido = pedidos.criar_pedido(
        checkout.usuario, str(checkout.pk), endereco=endereco,
        frete=Decimal(cotacao['valor']), tipo_entrega=cotacao['tipo'],
        prazo_entrega_dias=cotacao['prazo_dias'], previsao_entrega=date.fromisoformat(cotacao['previsao']),
    )
    checkout.pedido = pedido
    checkout.save(update_fields=['pedido'])
    return pedido


def _validar_estoque(pedido):
    itens = list(pedido.itens.order_by('produto_id'))
    produtos = {p.pk: p for p in Produto.objects.select_for_update().filter(
        pk__in=[item.produto_id for item in itens]).order_by('pk')}
    for item in itens:
        if produtos[item.produto_id].estoque < item.quantidade:
            raise ValidationError(f'Estoque insuficiente para "{item.nome_produto}". O pagamento não foi confirmado; seu carrinho foi preservado.')
    return itens


def _concluir(checkout, itens):
    """Executada na mesma transação da aprovação; uma única baixa por intenção."""
    for item in itens:
        alterados = Produto.objects.filter(pk=item.produto_id, estoque__gte=item.quantidade).update(
            estoque=F('estoque') - item.quantidade)
        if not alterados:
            raise ValidationError('O estoque mudou. O pagamento não foi confirmado.')
    carrinho = Carrinho.objects.select_for_update().filter(usuario=checkout.usuario).first()
    if carrinho:
        # Preserva itens novos e unidades acrescentadas depois de confirmar o pedido.
        for original in checkout.resumo_carrinho:
            item = carrinho.itens.select_for_update().filter(
                pk=original['item_id'], produto_id=original['produto_id']).first()
            if item:
                restante = item.quantidade - original['quantidade']
                if restante > 0:
                    item.quantidade = restante
                    item.save(update_fields=['quantidade'])
                else:
                    item.delete()
    checkout.estoque_baixado = True
    checkout.save(update_fields=['estoque_baixado'])


@transaction.atomic
def pagar(checkout, modalidade, dados=None):
    checkout = Checkout.objects.select_for_update().get(pk=checkout.pk)
    if not checkout.pedido_id:
        raise ValidationError('Confirme o resumo antes de pagar.')
    pedido = Pedido.objects.select_for_update().get(pk=checkout.pedido_id)
    if checkout.estoque_baixado:
        return pedido.pagamentos.filter(status=Pagamento.Status.APROVADO).first()
    itens = _validar_estoque(pedido)
    if modalidade == 'CARTAO':
        pagamento = pagamentos.pagar_com_cartao(checkout.usuario, pedido, **(dados or {}))
    elif modalidade == 'PIX':
        pagamento = pagamentos.gerar_pix(checkout.usuario, pedido)
    else:
        raise ValidationError('Modalidade de pagamento inválida.')
    if pagamento.status == Pagamento.Status.APROVADO:
        _concluir(checkout, itens)
    return pagamento


@transaction.atomic
def acao_pix(checkout, pagamento_id, *, cancelar=False):
    checkout = Checkout.objects.select_for_update().get(pk=checkout.pk)
    if checkout.estoque_baixado:
        return
    pagamento = Pagamento.objects.filter(pk=pagamento_id, pedido_id=checkout.pedido_id,
                                         modalidade=Pagamento.Modalidade.PIX).first()
    if not pagamento:
        raise ValidationError('PIX não encontrado neste checkout.')
    pedido = Pedido.objects.select_for_update().get(pk=checkout.pedido_id)
    if cancelar:
        pagamentos.cancelar_pix(checkout.usuario, pagamento)
    else:
        itens = _validar_estoque(pedido)
        pagamentos.confirmar_pix(checkout.usuario, pagamento)
        _concluir(checkout, itens)
