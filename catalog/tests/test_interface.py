"""Regressões da integração dos formulários da T05 com as views reais."""

import re
from decimal import Decimal
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from cart.models import ItemCarrinho

from .helpers import DadosCatalogoMixin


class FormulariosHTML(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.formularios = []
        self.atual = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == 'form':
            self.atual = {'atributos': atributos, 'campos': {}}
            self.formularios.append(self.atual)
        elif tag == 'input' and self.atual is not None:
            if atributos.get('name') and 'disabled' not in atributos:
                self.atual['campos'][atributos['name']] = atributos.get('value', '')

    def handle_endtag(self, tag):
        if tag == 'form':
            self.atual = None


class IntegracaoInterfaceTests(DadosCatalogoMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.usuario = get_user_model().objects.create_user('cliente_t05', password='senha-t05-123')

    def formulario(self, response, *, action=None, classe=None):
        formularios = FormulariosHTML(response.content.decode()).formularios
        encontrados = [
            formulario for formulario in formularios
            if (action is None or formulario['atributos'].get('action', '') == action)
            and (classe is None or classe in formulario['atributos'].get('class', '').split())
        ]
        self.assertEqual(len(encontrados), 1)
        return encontrados[0]

    def test_filtrar_preserva_palavra_buscada_e_categoria(self):
        livro = self.criar_livro(nome='Python na prática')
        self.criar_livro(nome='Outro livro')
        url = reverse('catalog:category', args=[self.cat_livros.pk])
        response = self.client.get(url, {'q': 'Python'})
        formulario = self.formulario(response, classe='filter-form')
        dados = formulario['campos'] | {'min_price': '10', 'max_price': '100'}

        response = self.client.get(formulario['atributos']['action'], dados)

        self.assertEqual(response.context['termo_busca'], 'Python')
        self.assertEqual(response.context['categoria_selecionada'], self.cat_livros)
        self.assertEqual(list(response.context['page_obj'].object_list), [livro.produto_ptr])

    def test_paginacao_preserva_categoria_passada_na_query(self):
        for numero in range(51):
            self.criar_livro(nome=f'Produto {numero:03}')
        self.criar_eletronico(nome='Produto fora da categoria')
        response = self.client.get('/', {'categoria': self.cat_livros.pk, 'q': 'Produto'})
        proxima = re.search(r'href="([^"]+)"[^>]*>Próxima</a>', response.content.decode())
        self.assertIsNotNone(proxima)

        response = self.client.get(urljoin('/', unescape(proxima.group(1))))

        self.assertEqual(response.context['categoria_selecionada'], self.cat_livros)
        self.assertEqual(response.context['total_produtos'], 51)
        self.assertEqual(len(response.context['page_obj'].object_list), 1)
        self.assertNotContains(response, 'Produto fora da categoria')

    def test_login_e_operacoes_dos_formularios_com_csrf_real(self):
        self.client = Client(enforce_csrf_checks=True)
        livro = self.criar_livro()
        detalhe = reverse('catalog:product_detail', args=[livro.pk])
        adicionar = reverse('cart:add', args=[livro.pk])
        carrinho = reverse('cart:detail')
        response = self.client.get(detalhe)
        formulario = self.formulario(response, action=adicionar)
        self.assertEqual(formulario['atributos']['method'], 'post')
        self.assertEqual(self.client.post(adicionar, {'quantidade': 1}).status_code, 403)

        response = self.client.post(adicionar, formulario['campos'], follow=True)
        self.assertContains(response, 'Entre para continuar')
        formulario = self.formulario(response, action='')
        self.assertEqual(formulario['campos']['next'], detalhe)
        response = self.client.post(reverse('login'), formulario['campos'] | {
            'username': self.usuario.username, 'password': 'senha-incorreta',
        })
        formulario = self.formulario(response, action='')
        self.assertEqual(formulario['campos']['username'], self.usuario.username)
        response = self.client.post(reverse('login'), formulario['campos'] | {
            'password': 'senha-t05-123',
        }, follow=True)
        self.assertEqual(response.request['PATH_INFO'], detalhe)

        formulario = self.formulario(response, action=adicionar)
        response = self.client.post(adicionar, formulario['campos'] | {'quantidade': 4}, follow=True)
        self.assertContains(response, 'Estoque insuficiente')
        self.assertContains(response, 'alert alert-danger')
        formulario = self.formulario(response, action=adicionar)
        response = self.client.post(adicionar, formulario['campos'] | {'quantidade': 2}, follow=True)
        self.assertEqual(response.request['PATH_INFO'], carrinho)
        item = ItemCarrinho.objects.get(carrinho__usuario=self.usuario)
        self.assertEqual(response.context['total'], Decimal('100.00'))

        atualizar = reverse('cart:update', args=[item.pk])
        formulario = self.formulario(response, action=atualizar)
        response = self.client.post(atualizar, formulario['campos'] | {'quantidade': 3}, follow=True)
        self.assertEqual(response.context['total'], Decimal('150.00'))
        remover = reverse('cart:remove', args=[item.pk])
        formulario = self.formulario(response, action=remover)
        response = self.client.post(remover, formulario['campos'], follow=True)
        self.assertContains(response, 'Seu carrinho está vazio')
        self.assertEqual(response.context['total'], Decimal('0.00'))

        formulario = self.formulario(response, action=reverse('logout'))
        self.client.post(reverse('logout'), formulario['campos'])
        self.assertRedirects(self.client.get(carrinho), f"{reverse('login')}?next={carrinho}")
