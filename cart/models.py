from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction


class Carrinho(models.Model):
    """Carrinho de compras de um usuário autenticado (UC04, UC05, UC11)."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrinho',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'carrinho'
        verbose_name_plural = 'carrinhos'

    def __str__(self):
        return f'Carrinho de {self.usuario}'

    @classmethod
    def do_usuario(cls, usuario):
        carrinho, _ = cls.objects.get_or_create(usuario=usuario)
        return carrinho

    def itens_com_produto(self):
        return self.itens.select_related('produto').order_by('id')

    @property
    def total(self):
        """total = soma dos subtotais (RN-08); carrinho vazio vale zero."""
        return sum((item.subtotal for item in self.itens_com_produto()), Decimal('0.00'))

    def adicionar(self, produto, quantidade):
        """Adiciona o produto ou soma à quantidade já existente (UC11, RN-06/RN-07)."""
        _validar_quantidade_positiva(quantidade)
        with transaction.atomic():
            item = self.itens.select_for_update().filter(produto=produto).first()
            quantidade_atual = item.quantidade if item else 0
            nova_quantidade = quantidade_atual + quantidade
            _validar_estoque(produto, nova_quantidade, quantidade_atual)
            if item:
                item.quantidade = nova_quantidade
                item.save(update_fields=['quantidade'])
            else:
                item = self.itens.create(produto=produto, quantidade=quantidade)
            self.save(update_fields=['atualizado_em'])
        return item


class ItemCarrinho(models.Model):
    """Produto do carrinho e sua quantidade. O preço é sempre lido de `Produto`."""

    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('catalog.Produto', on_delete=models.CASCADE, related_name='itens_carrinho')
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'item do carrinho'
        verbose_name_plural = 'itens do carrinho'
        constraints = [
            models.UniqueConstraint(fields=['carrinho', 'produto'], name='cart_item_produto_unico'),
            models.CheckConstraint(condition=models.Q(quantidade__gte=1), name='cart_item_quantidade_positiva'),
        ]

    def __str__(self):
        return f'{self.quantidade} × {self.produto}'

    @property
    def subtotal(self):
        """subtotal = preço unitário × quantidade (RN-08)."""
        return self.produto.preco * self.quantidade

    def alterar_quantidade(self, quantidade):
        """Altera a quantidade; quantidade 0 remove o item (decisão do grupo)."""
        if quantidade == 0:
            self.delete()
            return None
        _validar_quantidade_positiva(quantidade)
        _validar_estoque(self.produto, quantidade)
        self.quantidade = quantidade
        self.save(update_fields=['quantidade'])
        return self


def _validar_quantidade_positiva(quantidade):
    if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade < 1:
        raise ValidationError('A quantidade deve ser um número inteiro positivo.', code='quantidade_invalida')


def _validar_estoque(produto, quantidade_total, quantidade_no_carrinho=0):
    if produto.estoque <= 0:
        raise ValidationError(f'"{produto.nome}" está indisponível no momento.', code='sem_estoque')
    if quantidade_total > produto.estoque:
        mensagem = f'Estoque insuficiente para "{produto.nome}": há {produto.estoque} unidade(s) disponível(is).'
        if quantidade_no_carrinho:
            mensagem += f' Você já tem {quantidade_no_carrinho} no carrinho.'
        raise ValidationError(mensagem, code='estoque_insuficiente')
