"""Cadastro administrativo do catálogo (T02), usando o Django Admin.

Produtos são cadastrados, editados e excluídos apenas pelas telas de Livro e
Eletrônico. A tela "Produtos" é uma consulta geral somente leitura.
"""

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Autor,
    Categoria,
    Editora,
    Eletronico,
    Fabricante,
    Idioma,
    Livro,
    Produto,
)

CAMPOS_GERAIS = ('nome', 'descricao', 'categoria', 'preco', 'estoque')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pai', 'descricao')
    list_filter = ('pai',)
    list_select_related = ('pai',)
    search_fields = ('nome', 'descricao')


@admin.register(Idioma)
class IdiomaAdmin(admin.ModelAdmin):
    search_fields = ('nome',)


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'biografia')
    search_fields = ('nome',)


@admin.register(Editora)
class EditoraAdmin(admin.ModelAdmin):
    search_fields = ('nome',)


@admin.register(Fabricante)
class FabricanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


class ProdutoEspecializadoAdmin(admin.ModelAdmin):
    """Configuração comum das telas de Livro e Eletrônico."""

    list_display = ('nome', 'categoria', 'preco', 'estoque')
    list_filter = ('categoria',)
    list_select_related = ('categoria',)
    search_fields = ('nome', 'descricao')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'descricao':
            kwargs['widget'] = forms.Textarea(attrs={'rows': 4})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Livro)
class LivroAdmin(ProdutoEspecializadoAdmin):
    fieldsets = (
        ('Dados gerais', {'fields': CAMPOS_GERAIS}),
        ('Dados do livro', {
            'fields': ('isbn', 'numero_paginas', 'idioma', 'editora', 'autores'),
        }),
    )
    filter_horizontal = ('autores',)
    list_display = ProdutoEspecializadoAdmin.list_display + ('editora', 'idioma')
    list_filter = ('categoria', 'idioma', 'editora')
    list_select_related = ('categoria', 'editora', 'idioma')
    search_fields = ProdutoEspecializadoAdmin.search_fields + ('isbn', 'autores__nome')


@admin.register(Eletronico)
class EletronicoAdmin(ProdutoEspecializadoAdmin):
    fieldsets = (
        ('Dados gerais', {'fields': CAMPOS_GERAIS}),
        ('Dados do eletrônico', {
            'fields': ('modelo', 'garantia_meses', 'fabricante'),
        }),
    )
    list_display = ProdutoEspecializadoAdmin.list_display + ('fabricante', 'modelo')
    list_filter = ('categoria', 'fabricante')
    list_select_related = ('categoria', 'fabricante')
    search_fields = ProdutoEspecializadoAdmin.search_fields + ('modelo', 'fabricante__nome')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """Consulta geral, somente leitura, de todos os produtos."""

    list_display = ('nome', 'tipo', 'categoria', 'preco', 'estoque', 'link_edicao')
    list_filter = ('tipo', 'categoria')
    list_select_related = ('categoria',)
    search_fields = ('nome', 'descricao')

    @admin.display(description='editar')
    def link_edicao(self, obj):
        if obj.tipo == Produto.Tipo.LIVRO:
            url = reverse('admin:catalog_livro_change', args=[obj.pk])
        elif obj.tipo == Produto.Tipo.ELETRONICO:
            url = reverse('admin:catalog_eletronico_change', args=[obj.pk])
        else:
            return '—'
        return format_html('<a href="{}">Abrir {}</a>', url, obj.get_tipo_display())

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
