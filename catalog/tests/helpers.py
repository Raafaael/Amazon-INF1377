"""Dados de apoio compartilhados pelos testes de models e Admin."""

from decimal import Decimal

from ..models import Autor, Categoria, Editora, Eletronico, Fabricante, Idioma, Livro


class DadosCatalogoMixin:
    """Cria as entidades de apoio usadas pelos testes."""

    @classmethod
    def setUpTestData(cls):
        cls.cat_livros = Categoria.objects.create(nome='Livros')
        cls.cat_ficcao = Categoria.objects.create(nome='Ficção', pai=cls.cat_livros)
        cls.cat_eletronicos = Categoria.objects.create(nome='Eletrônicos')
        cls.idioma = Idioma.objects.create(nome='Português')
        cls.editora = Editora.objects.create(nome='Editora Teste')
        cls.autor = Autor.objects.create(nome='Autor Teste')
        cls.fabricante = Fabricante.objects.create(nome='Fabricante Teste')

    def dados_livro(self, **extra):
        dados = {
            'nome': 'Livro Teste',
            'descricao': 'Descrição do livro.',
            'preco': Decimal('50.00'),
            'estoque': 3,
            'categoria': self.cat_ficcao,
            'isbn': '000-0-00-000000-0',
            'numero_paginas': 100,
            'idioma': self.idioma,
            'editora': self.editora,
        }
        dados.update(extra)
        return dados

    def dados_eletronico(self, **extra):
        dados = {
            'nome': 'Eletrônico Teste',
            'descricao': 'Descrição do eletrônico.',
            'preco': Decimal('500.00'),
            'estoque': 2,
            'categoria': self.cat_eletronicos,
            'modelo': 'M-1',
            'garantia_meses': 12,
            'fabricante': self.fabricante,
        }
        dados.update(extra)
        return dados

    def criar_livro(self, **extra):
        livro = Livro.objects.create(**self.dados_livro(**extra))
        livro.autores.add(self.autor)
        return livro

    def criar_eletronico(self, **extra):
        return Eletronico.objects.create(**self.dados_eletronico(**extra))
