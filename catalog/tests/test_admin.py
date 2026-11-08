"""Cadastro, edi??o e permiss?es do Django Admin para o cat?logo."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Eletronico, Livro, Produto
from .helpers import DadosCatalogoMixin


class AdminCatalogoTests(DadosCatalogoMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_model = get_user_model()
        cls.admin = user_model.objects.create_superuser('admin', 'admin@exemplo.com', 'senha-teste')
        cls.cliente = user_model.objects.create_user('cliente', 'cliente@exemplo.com', 'senha-teste')

    def setUp(self):
        self.client.force_login(self.admin)

    def post_livro(self, **extra):
        dados = {
            'nome': 'Livro pelo Admin',
            'descricao': 'Cadastrado pelo Admin.',
            'categoria': self.cat_ficcao.pk,
            'preco': '59.90',
            'estoque': '4',
            'isbn': '000-0-00-000001-0',
            'numero_paginas': '150',
            'idioma': self.idioma.pk,
            'editora': self.editora.pk,
            'autores': [self.autor.pk],
            '_save': 'Salvar',
        }
        dados.update(extra)
        return self.client.post(reverse('admin:catalog_livro_add'), dados)

    def test_paginas_de_cadastro_abrem(self):
        for nome in ('admin:catalog_livro_add', 'admin:catalog_eletronico_add',
                     'admin:catalog_categoria_add'):
            with self.subTest(url=nome):
                self.assertEqual(self.client.get(reverse(nome)).status_code, 200)

    def test_cadastro_de_livro_valido(self):
        resposta = self.post_livro()
        self.assertEqual(resposta.status_code, 302)
        livro = Livro.objects.get(nome='Livro pelo Admin')
        self.assertEqual(livro.tipo, Produto.Tipo.LIVRO)
        self.assertEqual(list(livro.autores.all()), [self.autor])

    def test_cadastro_de_eletronico_valido(self):
        resposta = self.client.post(reverse('admin:catalog_eletronico_add'), {
            'nome': 'Eletrônico pelo Admin',
            'descricao': 'Cadastrado pelo Admin.',
            'categoria': self.cat_eletronicos.pk,
            'preco': '999.00',
            'estoque': '2',
            'modelo': 'ADM-1',
            'garantia_meses': '12',
            'fabricante': self.fabricante.pk,
            '_save': 'Salvar',
        })
        self.assertEqual(resposta.status_code, 302)
        eletronico = Eletronico.objects.get(nome='Eletrônico pelo Admin')
        self.assertEqual(eletronico.tipo, Produto.Tipo.ELETRONICO)

    def test_livro_sem_autor_nao_e_cadastrado(self):
        resposta = self.post_livro(autores=[])
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('autores', resposta.context['adminform'].form.errors)
        self.assertFalse(Livro.objects.exists())

    def test_livro_com_preco_fora_da_faixa_nao_e_cadastrado(self):
        resposta = self.post_livro(preco='10000.00')
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('preco', resposta.context['adminform'].form.errors)
        self.assertFalse(Livro.objects.exists())

    def test_usuario_comum_nao_acessa_cadastro(self):
        self.client.force_login(self.cliente)
        resposta = self.client.get(reverse('admin:catalog_livro_add'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('admin:login'), resposta['Location'])

    def test_edicao_de_livro_pelo_admin(self):
        livro = self.criar_livro()
        url = reverse('admin:catalog_livro_change', args=[livro.pk])
        resposta = self.client.post(url, {
            'nome': livro.nome,
            'descricao': livro.descricao,
            'categoria': livro.categoria_id,
            'preco': '75.00',
            'estoque': '9',
            'isbn': livro.isbn,
            'numero_paginas': livro.numero_paginas,
            'idioma': livro.idioma_id,
            'editora': livro.editora_id,
            'autores': [self.autor.pk],
            '_save': 'Salvar',
        })
        self.assertEqual(resposta.status_code, 302)
        livro.refresh_from_db()
        self.assertEqual(livro.preco, Decimal('75.00'))
        self.assertEqual(livro.estoque, 9)
        self.assertEqual(livro.tipo, Produto.Tipo.LIVRO)

    def test_edicao_de_eletronico_com_preco_invalido_preserva_valor(self):
        eletronico = self.criar_eletronico(preco=Decimal('500.00'))
        url = reverse('admin:catalog_eletronico_change', args=[eletronico.pk])
        dados = {
            'nome': eletronico.nome,
            'descricao': eletronico.descricao,
            'categoria': eletronico.categoria_id,
            'preco': '0',
            'estoque': '2',
            'modelo': eletronico.modelo,
            'garantia_meses': '12',
            'fabricante': eletronico.fabricante_id,
            '_save': 'Salvar',
        }
        resposta = self.client.post(url, dados)
        self.assertEqual(resposta.status_code, 200)
        eletronico.refresh_from_db()
        self.assertEqual(eletronico.preco, Decimal('500.00'))

        dados['preco'] = '650.00'
        resposta = self.client.post(url, dados)
        self.assertEqual(resposta.status_code, 302)
        eletronico.refresh_from_db()
        self.assertEqual(eletronico.preco, Decimal('650.00'))
        self.assertEqual(eletronico.tipo, Produto.Tipo.ELETRONICO)

    def test_produto_admin_e_somente_leitura(self):
        livro = self.criar_livro()
        self.assertEqual(
            self.client.get(reverse('admin:catalog_produto_changelist')).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse('admin:catalog_produto_add')).status_code, 403
        )
        url_change = reverse('admin:catalog_produto_change', args=[livro.pk])
        resposta = self.client.post(url_change, {'nome': 'Alterado', '_save': 'Salvar'})
        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(
            self.client.get(
                reverse('admin:catalog_produto_delete', args=[livro.pk])
            ).status_code,
            403,
        )
        livro.refresh_from_db()
        self.assertEqual(livro.nome, 'Livro Teste')
