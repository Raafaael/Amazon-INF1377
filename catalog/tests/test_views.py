from decimal import Decimal

from django.test import TestCase

from .helpers import DadosCatalogoMixin


class CatalogoPublicoTests(DadosCatalogoMixin, TestCase):
    def test_home_exibe_produtos_reais_do_catalogo(self):
        livro = self.criar_livro(nome='Livro de Ficção')
        eletronico = self.criar_eletronico(nome='Notebook Demo')

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Livro de Ficção')
        self.assertContains(response, 'Notebook Demo')
        self.assertContains(response, 'Catálogo')
        self.assertContains(response, 'R$')

    def test_busca_e_filtro_por_preco_sao_aplicados(self):
        self.criar_livro(nome='Python para Todos', preco=Decimal('75.00'))
        self.criar_livro(nome='Java em Foco', preco=Decimal('180.00'))
        self.criar_eletronico(nome='Smartphone Alpha', preco=Decimal('1200.00'))

        response = self.client.get('/?q=Python&min_price=10&max_price=100')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python para Todos')
        self.assertNotContains(response, 'Java em Foco')
        self.assertNotContains(response, 'Smartphone Alpha')
        self.assertContains(response, 'value="10"')
        self.assertContains(response, 'value="100"')

    def test_campos_de_preco_permanecem_preenchidos_com_decimais(self):
        response = self.client.get('/?min_price=42.75&max_price=99.99')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="42.75"')
        self.assertContains(response, 'value="99.99"')

    def test_categoria_e_detalhe_do_produto_respondem(self):
        livro = self.criar_livro(nome='Livro de Categoria')

        categoria_response = self.client.get(f'/categoria/{self.cat_livros.pk}/')
        detalhe_response = self.client.get(f'/produto/{livro.pk}/')

        self.assertEqual(categoria_response.status_code, 200)
        self.assertContains(categoria_response, 'Livro de Categoria')
        self.assertEqual(detalhe_response.status_code, 200)
        self.assertContains(detalhe_response, 'Livro de Categoria')
        self.assertContains(detalhe_response, 'Informações do livro')

    def test_filtro_invalido_e_paginacao_sao_tratados(self):
        for indice in range(60):
            self.criar_livro(nome=f'Livro {indice}', preco=Decimal('19.99'))

        response = self.client.get('/?min_price=abc&max_price=20')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Valor inválido para preço mínimo.')

        pagina_2 = self.client.get('/?page=2')
        self.assertEqual(pagina_2.status_code, 200)
        self.assertContains(pagina_2, 'Anterior')
        self.assertContains(pagina_2, '2')
