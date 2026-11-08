from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from catalog.tests.helpers import DadosCatalogoMixin

from .models import Carrinho, ItemCarrinho


class CarrinhoBaseTestCase(DadosCatalogoMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.usuario = User.objects.create_user('cliente_a', password='senha-teste-123')
        cls.outro_usuario = User.objects.create_user('cliente_b', password='senha-teste-123')

    def setUp(self):
        # estoque 3, preço 50,00 / estoque 2, preço 500,00
        self.livro = self.criar_livro()
        self.eletronico = self.criar_eletronico()

    def entrar(self, usuario=None):
        self.client.force_login(usuario or self.usuario)

    def adicionar(self, produto, quantidade):
        return self.client.post(reverse('cart:add', args=[produto.pk]), {'quantidade': quantidade}, follow=True)

    def item_de(self, usuario, produto):
        return ItemCarrinho.objects.get(carrinho__usuario=usuario, produto=produto)


class CarrinhoModelTests(CarrinhoBaseTestCase):
    def test_subtotal_e_total(self):
        carrinho = Carrinho.do_usuario(self.usuario)
        carrinho.adicionar(self.livro, 2)
        carrinho.adicionar(self.eletronico, 1)

        self.assertEqual(self.item_de(self.usuario, self.livro).subtotal, Decimal('100.00'))
        self.assertEqual(carrinho.total, Decimal('600.00'))

    def test_total_do_carrinho_vazio_e_zero(self):
        self.assertEqual(Carrinho.do_usuario(self.usuario).total, Decimal('0.00'))

    def test_quantidade_nao_inteira_ou_nao_positiva_e_rejeitada(self):
        carrinho = Carrinho.do_usuario(self.usuario)
        for quantidade in (0, -1, 1.5, '2'):
            with self.subTest(quantidade=quantidade), self.assertRaises(ValidationError):
                carrinho.adicionar(self.livro, quantidade)
        self.assertFalse(carrinho.itens.exists())

    def test_preco_e_lido_do_produto(self):
        carrinho = Carrinho.do_usuario(self.usuario)
        carrinho.adicionar(self.livro, 2)
        self.livro.preco = Decimal('60.00')
        self.livro.save()

        self.assertEqual(carrinho.total, Decimal('120.00'))


class AdicionarAoCarrinhoTests(CarrinhoBaseTestCase):
    def test_adiciona_produto(self):
        self.entrar()
        response = self.adicionar(self.livro, 2)

        self.assertRedirects(response, reverse('cart:detail'))
        self.assertEqual(self.item_de(self.usuario, self.livro).quantidade, 2)
        self.assertContains(response, 'foi adicionado ao carrinho')

    def test_inclusao_repetida_soma_quantidades(self):
        self.entrar()
        self.adicionar(self.livro, 1)
        self.adicionar(self.livro, 2)

        self.assertEqual(ItemCarrinho.objects.filter(carrinho__usuario=self.usuario).count(), 1)
        self.assertEqual(self.item_de(self.usuario, self.livro).quantidade, 3)

    def test_estoque_insuficiente(self):
        self.entrar()
        response = self.adicionar(self.livro, 4)

        self.assertRedirects(response, reverse('catalog:product_detail', args=[self.livro.pk]))
        self.assertContains(response, 'Estoque insuficiente')
        self.assertFalse(ItemCarrinho.objects.exists())

    def test_estoque_considera_quantidade_ja_no_carrinho(self):
        self.entrar()
        self.adicionar(self.livro, 2)
        response = self.adicionar(self.livro, 2)

        self.assertContains(response, 'Você já tem 2 no carrinho')
        self.assertEqual(self.item_de(self.usuario, self.livro).quantidade, 2)

    def test_produto_sem_estoque(self):
        esgotado = self.criar_livro(nome='Livro Esgotado', estoque=0)
        self.entrar()
        response = self.adicionar(esgotado, 1)

        self.assertContains(response, 'indisponível no momento')
        self.assertFalse(ItemCarrinho.objects.exists())

    def test_quantidade_invalida(self):
        self.entrar()
        for quantidade in ('0', '-2', 'abc', '1.5', ''):
            with self.subTest(quantidade=quantidade):
                response = self.adicionar(self.livro, quantidade)
                self.assertContains(response, 'número inteiro positivo')
        self.assertFalse(ItemCarrinho.objects.exists())

    def test_get_nao_altera_carrinho(self):
        self.entrar()
        response = self.client.get(reverse('cart:add', args=[self.livro.pk]))

        self.assertEqual(response.status_code, 405)
        self.assertFalse(ItemCarrinho.objects.exists())

    def test_anonimo_e_redirecionado_ao_login(self):
        response = self.client.post(reverse('cart:add', args=[self.livro.pk]), {'quantidade': 1})

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        self.assertFalse(ItemCarrinho.objects.exists())


class ConsultarCarrinhoTests(CarrinhoBaseTestCase):
    def test_carrinho_vazio(self):
        self.entrar()
        response = self.client.get(reverse('cart:detail'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seu carrinho está vazio')
        self.assertEqual(response.context['total'], Decimal('0.00'))

    def test_exibe_itens_subtotais_e_total(self):
        self.entrar()
        self.adicionar(self.livro, 2)
        self.adicionar(self.eletronico, 1)
        response = self.client.get(reverse('cart:detail'))

        self.assertContains(response, 'R$ 100,00')
        self.assertContains(response, 'R$ 600,00')
        self.assertEqual(response.context['total'], Decimal('600.00'))

    def test_anonimo_e_redirecionado_ao_login(self):
        response = self.client.get(reverse('cart:detail'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('cart:detail')}")


class AlterarERemoverItemTests(CarrinhoBaseTestCase):
    def setUp(self):
        super().setUp()
        self.item = Carrinho.do_usuario(self.usuario).adicionar(self.livro, 1)
        self.entrar()

    def atualizar(self, quantidade, item=None):
        item = item or self.item
        return self.client.post(reverse('cart:update', args=[item.pk]), {'quantidade': quantidade}, follow=True)

    def test_altera_quantidade(self):
        response = self.atualizar(3)

        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, 3)
        self.assertEqual(response.context['total'], Decimal('150.00'))

    def test_alterar_acima_do_estoque_e_rejeitado(self):
        response = self.atualizar(4)

        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, 1)
        self.assertContains(response, 'Estoque insuficiente')

    def test_alterar_com_quantidade_invalida_e_rejeitado(self):
        for quantidade in ('-1', 'abc', ''):
            with self.subTest(quantidade=quantidade):
                response = self.atualizar(quantidade)
                self.assertContains(response, 'número inteiro positivo')
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, 1)

    def test_quantidade_zero_remove_item(self):
        response = self.atualizar(0)

        self.assertFalse(ItemCarrinho.objects.filter(pk=self.item.pk).exists())
        self.assertContains(response, 'foi removido do carrinho')

    def test_remover_retira_todas_as_unidades_e_zera_total(self):
        self.atualizar(3)
        response = self.client.post(reverse('cart:remove', args=[self.item.pk]), follow=True)

        self.assertFalse(ItemCarrinho.objects.filter(pk=self.item.pk).exists())
        self.assertEqual(response.context['total'], Decimal('0.00'))
        self.assertContains(response, 'Seu carrinho está vazio')

    def test_remover_por_get_nao_altera_carrinho(self):
        response = self.client.get(reverse('cart:remove', args=[self.item.pk]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(ItemCarrinho.objects.filter(pk=self.item.pk).exists())


class IsolamentoEntreUsuariosTests(CarrinhoBaseTestCase):
    def setUp(self):
        super().setUp()
        self.item_de_a = Carrinho.do_usuario(self.usuario).adicionar(self.livro, 2)
        self.entrar(self.outro_usuario)

    def test_usuario_b_nao_ve_itens_de_a(self):
        response = self.client.get(reverse('cart:detail'))

        self.assertNotContains(response, self.livro.nome)
        self.assertEqual(response.context['total'], Decimal('0.00'))

    def test_usuario_b_nao_altera_item_de_a(self):
        response = self.client.post(reverse('cart:update', args=[self.item_de_a.pk]), {'quantidade': 1})

        self.assertEqual(response.status_code, 404)
        self.item_de_a.refresh_from_db()
        self.assertEqual(self.item_de_a.quantidade, 2)

    def test_usuario_b_nao_remove_item_de_a(self):
        response = self.client.post(reverse('cart:remove', args=[self.item_de_a.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(ItemCarrinho.objects.filter(pk=self.item_de_a.pk).exists())

    def test_adicionar_vai_para_o_carrinho_do_proprio_usuario(self):
        self.client.post(reverse('cart:add', args=[self.livro.pk]), {'quantidade': 1})

        self.assertEqual(self.item_de(self.usuario, self.livro).quantidade, 2)
        self.assertEqual(self.item_de(self.outro_usuario, self.livro).quantidade, 1)
