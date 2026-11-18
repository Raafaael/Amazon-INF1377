from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Pedido
from orders.services import atualizar_status


TABELA = {
    'PADRAO': (Decimal('15.90'), 7),
    'EXPRESSA': (Decimal('29.90'), 3),
}


def cotar_frete(cep, modalidade, hoje=None):
    """Retorna uma cotação fictícia fixa, sem sorteio ou dependência externa."""
    if modalidade not in TABELA:
        raise ValidationError('Modalidade de entrega inválida.')
    valor, prazo_padrao = TABELA[modalidade]

    return {
        'valor': valor,
        'prazo_dias': prazo_padrao,
        'tipo': modalidade,
        'previsao': (hoje or timezone.localdate()) + timedelta(days=prazo_padrao),
    }


def avancar_entrega(pedido, usuario):
    """Avança a entrega simulada usando exclusivamente o contrato de pedidos."""
    if not usuario.is_authenticated or not usuario.is_staff:
        raise ValidationError('Somente administradores podem simular a entrega.')

    proximo = {
        Pedido.Status.PAGAMENTO_APROVADO: Pedido.Status.EM_PREPARACAO,
        Pedido.Status.EM_PREPARACAO: Pedido.Status.ENVIADO,
        Pedido.Status.ENVIADO: Pedido.Status.ENTREGUE,
    }.get(pedido.status)
    if proximo is None:
        raise ValidationError('Este pedido não pode avançar na entrega simulada.')

    observacoes = {
        Pedido.Status.EM_PREPARACAO: 'Pedido aprovado e em preparação.',
        Pedido.Status.ENVIADO: 'Pedido enviado na simulação de entrega.',
        Pedido.Status.ENTREGUE: 'Pedido entregue na simulação.',
    }
    return atualizar_status(
        pedido,
        proximo,
        origem='entrega',
        usuario=usuario,
        observacao=observacoes[proximo],
    )
