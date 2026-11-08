"""Models do catálogo (T02).

Referências: UC01, SRS v1.1 RF-CAT-01 a RF-CAT-09 e RN-01 a RN-05;
diagrama de tabelas, bloco "Catálogo de Produtos".

Livro e Eletronico usam herança multi-tabela a partir de Produto, como no
modelo relacional (a PK de Livro/Eletronico é também FK para Produto).
Consulte catalog/CONTRATO.md para o uso destes models pelos demais apps.
"""

from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

PRECO_MINIMO_EXCLUSIVO = Decimal('0.00')
PRECO_MAXIMO_EXCLUSIVO = Decimal('10000.00')
MENSAGEM_FAIXA_PRECO = (
    'O preço deve ser maior que R$ 0,00 e menor que R$ 10.000,00.'
)


def validar_faixa_preco(valor):
    """RN-02: o preço deve ser > R$ 0,00 e < R$ 10.000,00 (limites exclusivos)."""
    if valor is None:
        return
    if not (PRECO_MINIMO_EXCLUSIVO < valor < PRECO_MAXIMO_EXCLUSIVO):
        raise ValidationError(MENSAGEM_FAIXA_PRECO, code='preco_fora_da_faixa')


class Categoria(models.Model):
    nome = models.CharField('nome', max_length=100)
    descricao = models.CharField('descrição', max_length=100, blank=True)
    pai = models.ForeignKey(
        'self',
        verbose_name='categoria pai',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='subcategorias',
        help_text='Deixe em branco para uma categoria principal.',
    )

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'
        ordering = ['nome']

    def __str__(self):
        if self.pai_id:
            return f'{self.pai} > {self.nome}'
        return self.nome

    def clean(self):
        super().clean()
        if self.pai_id is None or self.pk is None:
            return
        # Impede que a categoria seja pai de si mesma ou de um ancestral seu.
        atual = self.pai
        while atual is not None:
            if atual.pk == self.pk:
                raise ValidationError(
                    {'pai': 'Uma categoria não pode ser subcategoria de si mesma '
                            'nem de uma de suas subcategorias.'}
                )
            atual = atual.pai


class Idioma(models.Model):
    nome = models.CharField('nome', max_length=200, unique=True)

    class Meta:
        verbose_name = 'idioma'
        verbose_name_plural = 'idiomas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Autor(models.Model):
    nome = models.CharField('nome', max_length=100)
    biografia = models.CharField('biografia', max_length=100, blank=True)

    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Editora(models.Model):
    nome = models.CharField('nome', max_length=30)

    class Meta:
        verbose_name = 'editora'
        verbose_name_plural = 'editoras'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Fabricante(models.Model):
    nome = models.CharField('nome', max_length=30)
    descricao = models.CharField('descrição', max_length=100, blank=True)

    class Meta:
        verbose_name = 'fabricante'
        verbose_name_plural = 'fabricantes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """Dados gerais de qualquer item do catálogo.

    Não deve ser criado diretamente: todo produto é um Livro ou um Eletronico
    (RN-01). O campo ``tipo`` é preenchido pela subclasse.
    """

    class Tipo(models.TextChoices):
        LIVRO = 'LIVRO', 'Livro'
        ELETRONICO = 'ELETRONICO', 'Eletrônico'

    nome = models.CharField('nome', max_length=100)
    descricao = models.CharField('descrição', max_length=500)
    preco = models.DecimalField(
        'preço unitário',
        max_digits=12,
        decimal_places=2,
        validators=[validar_faixa_preco],
        help_text='Maior que R$ 0,00 e menor que R$ 10.000,00.',
    )
    estoque = models.PositiveIntegerField('quantidade em estoque', default=0)
    categoria = models.ForeignKey(
        Categoria,
        verbose_name='categoria',
        on_delete=models.PROTECT,
        related_name='produtos',
    )
    tipo = models.CharField(
        'tipo', max_length=10, choices=Tipo.choices, editable=False
    )

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'
        ordering = ['nome', 'id']
        constraints = [
            models.CheckConstraint(
                condition=Q(preco__gt=PRECO_MINIMO_EXCLUSIVO)
                & Q(preco__lt=PRECO_MAXIMO_EXCLUSIVO),
                name='catalog_produto_preco_faixa_valida',
                violation_error_message=MENSAGEM_FAIXA_PRECO,
            ),
            # Restringe apenas o VALOR do tipo; não garante a existência da
            # linha filha em Livro/Eletronico (ver save() e CONTRATO.md).
            models.CheckConstraint(
                condition=Q(tipo__in=['LIVRO', 'ELETRONICO']),
                name='catalog_produto_tipo_valido',
            ),
        ]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if type(self) is Produto:
            if self._state.adding:
                raise ValueError(
                    'Não é possível criar um Produto genérico: cadastre como Livro '
                    'ou Eletrônico.'
                )
            tipo_atual = Produto.objects.filter(pk=self.pk).values_list(
                'tipo', flat=True
            ).first()
            if tipo_atual is not None and self.tipo != tipo_atual:
                raise ValueError(
                    'Não é possível alterar o tipo de um Produto existente.'
                )
        super().save(*args, **kwargs)

    @property
    def em_estoque(self):
        """Indica apenas disponibilidade (estoque > 0); não significa 'ativo'."""
        return self.estoque > 0

    def especializacao(self):
        """Retorna o Livro ou Eletronico correspondente, ou None se não houver."""
        if type(self) is not Produto:
            return self
        for nome_relacao in ('livro', 'eletronico'):
            try:
                return getattr(self, nome_relacao)
            except ObjectDoesNotExist:
                continue
        return None


class EspecializacaoProdutoMixin:
    """Comportamento comum a Livro e Eletronico (classe Python simples)."""

    TIPO = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define o tipo já na criação da instância, para que full_clean() de
        # um objeto ainda não salvo encontre o valor correto. A checagem em
        # __dict__ evita consultar o banco quando 'tipo' foi adiado (.only()).
        if 'tipo' in self.__dict__ and not self.tipo:
            self.tipo = self.TIPO

    def save(self, *args, **kwargs):
        self.tipo = self.TIPO
        super().save(*args, **kwargs)


class Livro(EspecializacaoProdutoMixin, Produto):
    TIPO = Produto.Tipo.LIVRO

    isbn = models.CharField('ISBN', max_length=30)
    numero_paginas = models.PositiveIntegerField(
        'número de páginas', validators=[MinValueValidator(1)]
    )
    idioma = models.ForeignKey(
        Idioma,
        verbose_name='idioma',
        on_delete=models.PROTECT,
        related_name='livros',
    )
    editora = models.ForeignKey(
        Editora,
        verbose_name='editora',
        on_delete=models.PROTECT,
        related_name='livros',
    )
    # Relacional: Autor_Livro (1..* autores por livro). A obrigatoriedade do
    # M2M é garantida no formulário (blank=False), não pelo banco.
    autores = models.ManyToManyField(
        Autor, verbose_name='autores', related_name='livros'
    )

    class Meta:
        verbose_name = 'livro'
        verbose_name_plural = 'livros'


class Eletronico(EspecializacaoProdutoMixin, Produto):
    TIPO = Produto.Tipo.ELETRONICO

    modelo = models.CharField('modelo', max_length=100)
    garantia_meses = models.PositiveIntegerField('garantia (meses)')
    fabricante = models.ForeignKey(
        Fabricante,
        verbose_name='fabricante',
        on_delete=models.PROTECT,
        related_name='eletronicos',
    )

    class Meta:
        verbose_name = 'eletrônico'
        verbose_name_plural = 'eletrônicos'
