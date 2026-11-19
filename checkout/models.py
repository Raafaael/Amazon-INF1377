import uuid

from django.conf import settings
from django.db import models


class Checkout(models.Model):
    """Uma intenção de compra; os dados financeiros definitivos ficam em Pedido."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    endereco = models.ForeignKey('addresses.Endereco', null=True, blank=True, on_delete=models.SET_NULL)
    endereco_dados = models.JSONField(default=dict, blank=True)
    resumo_carrinho = models.JSONField(default=list)
    cotacoes = models.JSONField(default=dict, blank=True)
    modalidade = models.CharField(max_length=10, blank=True)
    pedido = models.OneToOneField('orders.Pedido', null=True, blank=True, on_delete=models.PROTECT,
                                 related_name='checkout')
    estoque_baixado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
