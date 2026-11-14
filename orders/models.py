from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Pedido(models.Model):
    """Retrato financeiro da compra, independente de mudanças no catálogo."""

    class Status(models.TextChoices):
        AGUARDANDO_PAGAMENTO = 'AGUARDANDO_PAGAMENTO', 'Aguardando pagamento'
        PAGAMENTO_RECUSADO = 'PAGAMENTO_RECUSADO', 'Pagamento recusado'
        PAGAMENTO_APROVADO = 'PAGAMENTO_APROVADO', 'Pagamento aprovado'
        EM_PREPARACAO = 'EM_PREPARACAO', 'Em preparação'
        ENVIADO = 'ENVIADO', 'Enviado'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        CANCELADO = 'CANCELADO', 'Cancelado'

    class TipoEntrega(models.TextChoices):
        PADRAO = 'PADRAO', 'Padrão'
        EXPRESSA = 'EXPRESSA', 'Expressa'
        AGENDADA = 'AGENDADA', 'Agendada'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos')
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.AGUARDANDO_PAGAMENTO)
    chave_checkout = models.CharField(max_length=64)
    subtotal_itens = models.DecimalField(max_digits=12, decimal_places=2)
    frete = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_entrega = models.CharField(max_length=10, choices=TipoEntrega.choices, blank=True)
    endereco_entrega = models.TextField(blank=True)
    endereco_dados = models.JSONField(default=dict, blank=True)
    prazo_entrega_dias = models.PositiveIntegerField(null=True, blank=True)
    previsao_entrega = models.DateField(null=True, blank=True)
    enviado_em = models.DateTimeField(null=True, blank=True)
    entregue_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em', '-id']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'chave_checkout'], name='orders_checkout_unico_usuario'),
            models.CheckConstraint(condition=Q(subtotal_itens__gte=0) & Q(frete__gte=0) & Q(total__gte=0), name='orders_valores_nao_negativos'),
        ]

    def __str__(self):
        return f'Pedido #{self.pk}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('catalog.Produto', on_delete=models.PROTECT, related_name='itens_pedido')
    nome_produto = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'item do pedido'
        verbose_name_plural = 'itens do pedido'
        constraints = [
            models.UniqueConstraint(fields=['pedido', 'produto'], name='orders_item_produto_unico'),
            models.CheckConstraint(condition=Q(quantidade__gte=1) & Q(preco_unitario__gt=0) & Q(subtotal__gt=0), name='orders_item_valores_validos'),
        ]

    def __str__(self):
        return f'{self.quantidade} × {self.nome_produto}'


class HistoricoStatusPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historico')
    status = models.CharField(max_length=24, choices=Pedido.Status.choices)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['data_alteracao', 'id']
        verbose_name = 'histórico de status do pedido'
        verbose_name_plural = 'históricos de status dos pedidos'

    def __str__(self):
        return f'{self.pedido} — {self.get_status_display()}'
