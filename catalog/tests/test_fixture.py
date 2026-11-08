"""Integridade dos dados fict?cios carregados por loaddata."""

from django.test import TestCase

from ..models import Categoria, Eletronico, Livro, Produto


class FixtureDemoTests(TestCase):
    fixtures = ['catalogo_demo']

    def test_fixture_tem_livros_e_eletronicos(self):
        self.assertGreaterEqual(Livro.objects.count(), 1)
        self.assertGreaterEqual(Eletronico.objects.count(), 1)

    def test_cada_produto_tem_o_filho_do_seu_tipo(self):
        ids_livros = set(Livro.objects.values_list('pk', flat=True))
        ids_eletronicos = set(Eletronico.objects.values_list('pk', flat=True))
        self.assertFalse(ids_livros & ids_eletronicos)
        for produto in Produto.objects.all():
            with self.subTest(produto=produto.nome):
                if produto.tipo == Produto.Tipo.LIVRO:
                    self.assertIn(produto.pk, ids_livros)
                else:
                    self.assertEqual(produto.tipo, Produto.Tipo.ELETRONICO)
                    self.assertIn(produto.pk, ids_eletronicos)

    def test_cada_livro_tem_ao_menos_um_autor(self):
        for livro in Livro.objects.all():
            with self.subTest(livro=livro.nome):
                self.assertGreaterEqual(livro.autores.count(), 1)

    def test_registros_da_fixture_passam_na_validacao(self):
        for objeto in [*Livro.objects.all(), *Eletronico.objects.all(),
                       *Categoria.objects.all()]:
            with self.subTest(objeto=str(objeto)):
                objeto.full_clean()

    def test_fixture_tem_produto_sem_estoque(self):
        self.assertTrue(Produto.objects.filter(estoque=0).exists())
