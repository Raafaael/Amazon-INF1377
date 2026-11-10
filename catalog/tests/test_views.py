import re
from decimal import Decimal
from html import unescape
from urllib.parse import urljoin

from django.test import TestCase

from catalog.models import Categoria, Fabricante

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

    def test_categoria_vazia_exibe_estado_sem_produtos(self):
        categoria = Categoria.objects.create(nome='Categoria vazia')

        response = self.client.get(f'/categoria/{categoria.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_produtos'], 0)
        self.assertContains(response, 'Não encontramos produtos')

    def test_fabricante_e_faixa_de_preco_sao_combinados(self):
        outro_fabricante = Fabricante.objects.create(nome='Outro fabricante')
        esperado = self.criar_eletronico(nome='Modelo esperado', preco=Decimal('500.00'))
        self.criar_eletronico(nome='Acima do limite', preco=Decimal('1500.00'))
        self.criar_eletronico(
            nome='Fabricante diferente', preco=Decimal('500.00'),
            fabricante=outro_fabricante,
        )

        response = self.client.get(
            '/', {'fabricante': self.fabricante.pk, 'min_price': '400', 'max_price': '600'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['page_obj'].object_list), [esperado.produto_ptr])
        self.assertContains(response, 'Modelo esperado')
        self.assertNotContains(response, 'Acima do limite')
        self.assertNotContains(response, 'Fabricante diferente')

    def test_categoria_e_detalhe_do_produto_respondem(self):
        livro = self.criar_livro(nome='Livro de Categoria')

        categoria_response = self.client.get(f'/categoria/{self.cat_livros.pk}/')
        detalhe_response = self.client.get(f'/produto/{livro.pk}/')

        self.assertEqual(categoria_response.status_code, 200)
        self.assertContains(categoria_response, 'Livro de Categoria')
        self.assertEqual(detalhe_response.status_code, 200)
        self.assertContains(detalhe_response, 'Livro de Categoria')
        self.assertContains(detalhe_response, 'Sobre o livro')

    def test_filtro_invalido_exibe_erro(self):
        response = self.client.get('/?min_price=abc&max_price=20')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Valor inválido para preço mínimo.')

    def test_paginacao_divide_produtos_e_preserva_categoria_e_filtros(self):
        for indice in range(51):
            self.criar_livro(nome=f'Python {indice:03}', preco=Decimal('19.99'))
        self.criar_eletronico(nome='Python fora da categoria', preco=Decimal('19.99'))
        self.criar_livro(nome='Outro livro', preco=Decimal('19.99'))

        url = f'/categoria/{self.cat_livros.pk}/?q=Python&min_price=10&max_price=20'
        pagina_1 = self.client.get(url)
        self.assertEqual(pagina_1.status_code, 200)
        self.assertEqual(pagina_1.context['total_produtos'], 51)
        self.assertEqual(len(pagina_1.context['page_obj'].object_list), 50)
        self.assertContains(pagina_1, 'Python 000')
        self.assertNotContains(pagina_1, 'Python 050')

        proxima = re.search(r'href="([^"]+)"[^>]*>Próxima</a>', pagina_1.content.decode())
        self.assertIsNotNone(proxima)
        pagina_2 = self.client.get(urljoin(url, unescape(proxima.group(1))))
        self.assertEqual(pagina_2.status_code, 200)
        self.assertEqual(pagina_2.context['page_obj'].number, 2)
        self.assertEqual(len(pagina_2.context['page_obj'].object_list), 1)
        self.assertContains(pagina_2, 'Python 050')
        self.assertNotContains(pagina_2, 'Python fora da categoria')
        self.assertNotContains(pagina_2, 'Outro livro')

    def test_pagina_invalida_usa_primeira_e_pagina_alta_usa_ultima(self):
        for indice in range(51):
            self.criar_livro(nome=f'Livro {indice:03}')

        self.assertEqual(self.client.get('/?page=abc').context['page_obj'].number, 1)
        self.assertEqual(self.client.get('/?page=99').context['page_obj'].number, 2)
