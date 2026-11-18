from datetime import timedelta
from decimal import Decimal
from random import randint

from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Pedido
from orders.services import atualizar_status


FAIXAS_FRETE_CENTAVOS = {
    'PADRAO': (1200, 2000, 7),
    'EXPRESSA': (2500, 3500, 3),
}


def cotar_frete(cep, modalidade, hoje=None):
    """Retorna uma cotação fictícia aleatória dentro dos limites da modalidade."""
    if modalidade not in FAIXAS_FRETE_CENTAVOS:
        raise ValidationError('Modalidade de entrega inválida.')
    minimo, maximo, prazo_padrao = FAIXAS_FRETE_CENTAVOS[modalidade]
    valor = Decimal(randint(minimo, maximo)).scaleb(-2)

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
