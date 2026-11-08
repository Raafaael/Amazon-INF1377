"""Valida??es, tipos e rela??es dos models do cat?logo."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from ..models import Categoria, Eletronico, Livro, Produto
from .helpers import DadosCatalogoMixin


class ValidacaoPrecoTests(DadosCatalogoMixin, TestCase):
    def assert_preco_invalido(self, valor):
        livro = Livro(**self.dados_livro(preco=Decimal(valor)))
        with self.assertRaises(ValidationError) as ctx:
            livro.full_clean()
        self.assertIn('preco', ctx.exception.message_dict)

    def test_preco_zero_e_invalido(self):
        self.assert_preco_invalido('0')

    def test_preco_negativo_e_invalido(self):
        self.assert_preco_invalido('-1.00')

    def test_preco_dez_mil_e_invalido(self):
        self.assert_preco_invalido('10000.00')

    def test_preco_com_tres_casas_decimais_e_invalido(self):
        self.assert_preco_invalido('10.001')

    def test_precos_nos_limites_internos_sao_validos(self):
        for valor in ('0.01', '9999.99'):
            with self.subTest(valor=valor):
                Livro(**self.dados_livro(preco=Decimal(valor))).full_clean()

    def test_banco_rejeita_preco_fora_da_faixa(self):
        # create() não chama full_clean(); a CheckConstraint do banco barra.
        for valor in ('0', '10000'):
            with self.subTest(valor=valor):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Livro.objects.create(**self.dados_livro(preco=Decimal(valor)))


class ValidacaoCamposTests(DadosCatalogoMixin, TestCase):
    def test_estoque_negativo_e_invalido(self):
        livro = Livro(**self.dados_livro(estoque=-1))
        with self.assertRaises(ValidationError) as ctx:
            livro.full_clean()
        self.assertIn('estoque', ctx.exception.message_dict)

    def test_campos_gerais_obrigatorios(self):
        livro = Livro(**self.dados_livro(nome='', descricao='', categoria=None))
        with self.assertRaises(ValidationError) as ctx:
            livro.full_clean()
        for campo in ('nome', 'descricao', 'categoria'):
            self.assertIn(campo, ctx.exception.message_dict)

    def test_livro_exige_dados_especificos(self):
        livro = Livro(**self.dados_livro(isbn='', idioma=None, editora=None))
        with self.assertRaises(ValidationError) as ctx:
            livro.full_clean()
        for campo in ('isbn', 'idioma', 'editora'):
            self.assertIn(campo, ctx.exception.message_dict)

    def test_livro_exige_ao_menos_uma_pagina(self):
        livro = Livro(**self.dados_livro(numero_paginas=0))
        with self.assertRaises(ValidationError) as ctx:
            livro.full_clean()
        self.assertIn('numero_paginas', ctx.exception.message_dict)

    def test_eletronico_exige_dados_especificos(self):
        eletronico = Eletronico(**self.dados_eletronico(modelo='', fabricante=None))
        with self.assertRaises(ValidationError) as ctx:
            eletronico.full_clean()
        for campo in ('modelo', 'fabricante'):
            self.assertIn(campo, ctx.exception.message_dict)


class TipoEConsistenciaTests(DadosCatalogoMixin, TestCase):
    def test_tipo_definido_antes_de_salvar(self):
        livro = Livro(**self.dados_livro())
        eletronico = Eletronico(**self.dados_eletronico())
        self.assertEqual(livro.tipo, Produto.Tipo.LIVRO)
        self.assertEqual(eletronico.tipo, Produto.Tipo.ELETRONICO)
        livro.full_clean()
        eletronico.full_clean()

    def test_tipo_e_mantido_ao_salvar(self):
        livro = self.criar_livro()
        livro.tipo = Produto.Tipo.ELETRONICO
        livro.save()
        livro.refresh_from_db()
        self.assertEqual(livro.tipo, Produto.Tipo.LIVRO)

    def test_produto_generico_nao_pode_ser_criado(self):
        produto = Produto(
            nome='Genérico', descricao='x', preco=Decimal('10.00'),
            categoria=self.cat_livros, tipo=Produto.Tipo.LIVRO,
        )
        with self.assertRaises(ValueError):
            produto.save()
        self.assertFalse(Produto.objects.exists())

    def test_produto_existente_pode_ser_atualizado_pelo_pai(self):
        livro = self.criar_livro(estoque=5)
        produto = Produto.objects.get(pk=livro.pk)
        produto.estoque = 4
        produto.save()
        livro.refresh_from_db()
        self.assertEqual(livro.estoque, 4)

    def test_tipo_nao_pode_ser_alterado_pelo_produto_pai(self):
        livro = self.criar_livro()
        produto = Produto.objects.get(pk=livro.pk)
        produto.tipo = Produto.Tipo.ELETRONICO

        with self.assertRaisesMessage(
            ValueError, 'Não é possível alterar o tipo de um Produto existente.'
        ):
            produto.save()

        livro.refresh_from_db()
        self.assertEqual(livro.tipo, Produto.Tipo.LIVRO)
        self.assertIsInstance(Produto.objects.get(pk=livro.pk).especializacao(), Livro)

    def test_consulta_geral_traz_ambos_os_tipos_com_especializacao(self):
        livro = self.criar_livro()
        eletronico = self.criar_eletronico()
        produtos = {p.pk: p for p in Produto.objects.all()}
        self.assertEqual(set(produtos), {livro.pk, eletronico.pk})

        esp_livro = produtos[livro.pk].especializacao()
        esp_eletronico = produtos[eletronico.pk].especializacao()
        self.assertIsInstance(esp_livro, Livro)
        self.assertIsInstance(esp_eletronico, Eletronico)
        self.assertEqual(produtos[livro.pk].livro.isbn, livro.isbn)
        self.assertEqual(produtos[eletronico.pk].eletronico.modelo, 'M-1')

    def test_em_estoque(self):
        self.assertTrue(self.criar_livro(estoque=1).em_estoque)
        self.assertFalse(self.criar_eletronico(estoque=0).em_estoque)


class CategoriaTests(DadosCatalogoMixin, TestCase):
    def test_subcategorias(self):
        self.assertEqual(list(self.cat_livros.subcategorias.all()), [self.cat_ficcao])
        self.assertEqual(str(self.cat_ficcao), 'Livros > Ficção')

    def test_categoria_nao_pode_ser_pai_de_si_mesma(self):
        self.cat_livros.pai = self.cat_livros
        with self.assertRaises(ValidationError) as ctx:
            self.cat_livros.full_clean()
        self.assertIn('pai', ctx.exception.message_dict)

    def test_ciclo_entre_categorias_e_invalido(self):
        self.cat_livros.pai = self.cat_ficcao  # Ficção já é filha de Livros
        with self.assertRaises(ValidationError) as ctx:
            self.cat_livros.full_clean()
        self.assertIn('pai', ctx.exception.message_dict)

    def test_categoria_com_produtos_nao_pode_ser_excluida(self):
        self.criar_livro()
        with self.assertRaises(ProtectedError):
            self.cat_ficcao.delete()
