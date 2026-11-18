"""Pagamentos SIMULADOS: nenhuma cobrança real, nenhum dado sensível de cartão persistido."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

MAX_PARCELAS = 12


class Pagamento(models.Model):
    """Tentativa de pagamento de um pedido; o valor é copiado de `pedido.total`."""

    class Modalidade(models.TextChoices):
        CARTAO = 'CARTAO', 'Cartão (fictício)'
        PIX = 'PIX', 'PIX (simulado)'

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADO = 'APROVADO', 'Aprovado'
        RECUSADO = 'RECUSADO', 'Recusado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    pedido = models.ForeignKey('orders.Pedido', on_delete=models.PROTECT, related_name='pagamentos')
    modalidade = models.CharField(max_length=6, choices=Modalidade.choices)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    mensagem = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em', '-id']
        verbose_name = 'pagamento'
        verbose_name_plural = 'pagamentos'
        constraints = [
            models.CheckConstraint(condition=Q(valor__gt=0), name='payments_valor_positivo'),
            models.UniqueConstraint(fields=['pedido'], condition=Q(status='APROVADO'),
                                    name='payments_um_aprovado_por_pedido'),
        ]

    def __str__(self):
        return f'Pagamento #{self.pk} ({self.get_modalidade_display()}) — {self.get_status_display()}'


class PagamentoCartao(models.Model):
    """Especialização para cartão: guarda apenas bandeira, últimos 4 dígitos e parcelas."""

    pagamento = models.OneToOneField(Pagamento, on_delete=models.CASCADE, primary_key=True,
                                     related_name='cartao')
    bandeira = models.CharField(max_length=20)
    ultimos_digitos = models.CharField(max_length=4)
    parcelas = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(MAX_PARCELAS)])
    valor_parcela = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'pagamento com cartão'
        verbose_name_plural = 'pagamentos com cartão'
        constraints = [
            models.CheckConstraint(condition=Q(parcelas__gte=1) & Q(parcelas__lte=MAX_PARCELAS),
                                   name='payments_parcelas_validas'),
        ]

    @property
    def cartao_mascarado(self):
        return f'•••• •••• •••• {self.ultimos_digitos}'


class PagamentoPix(models.Model):
    """Especialização para PIX: código de demonstração NÃO pagável e expiração."""

    pagamento = models.OneToOneField(Pagamento, on_delete=models.CASCADE, primary_key=True,
                                     related_name='pix')
    codigo = models.CharField(max_length=40, unique=True)
    expira_em = models.DateTimeField()

    class Meta:
        verbose_name = 'pagamento PIX'
        verbose_name_plural = 'pagamentos PIX'

    @property
    def expirado(self):
        return timezone.now() >= self.expira_em

    @property
    def conteudo_qr(self):
        """Texto livre (não é BR Code/EMV), portanto não pode ser lido como cobrança PIX."""
        p = self.pagamento
        return (f'PIX SIMULADO - NAO PAGAVEL | Amazon Academico | Pedido #{p.pedido_id} | '
                f'Valor R$ {p.valor} | Codigo {self.codigo}')
