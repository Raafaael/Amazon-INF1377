"""Fluxos HTTP reais da T10, usando os contratos dos quatro módulos."""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from addresses.models import Endereco
from cart.models import Carrinho
from catalog.models import Produto
from catalog.tests.helpers import DadosCatalogoMixin
from catalog.tests.test_interface import FormulariosHTML
from orders.models import Pedido
from payments.models import Pagamento, PagamentoPix

from .models import Checkout


class CheckoutTests(DadosCatalogoMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.usuario = get_user_model().objects.create_user('davi_t10', password='senha-teste')
        cls.outro = get_user_model().objects.create_user('outro_t10', password='senha-teste')
        dados = dict(cep='20040-020', logradouro='Rua Fictícia', numero='10', bairro='Centro',
                     cidade='Rio de Janeiro', estado='RJ', tipo='CASA')
        cls.endereco = Endereco.objects.create(usuario=cls.usuario, **dados)
        cls.endereco_alheio = Endereco.objects.create(usuario=cls.outro, **dados)

    def setUp(self):
        self.client.force_login(self.usuario)
        self.livro = self.criar_livro(estoque=10)
        self.carrinho = Carrinho.do_usuario(self.usuario)
        self.item = self.carrinho.adicionar(self.livro, 2)

    def url(self, nome, *extra):
        return reverse(f'checkout:{nome}', args=[self.checkout.pk, *extra])

    def iniciar(self):
        response = self.client.post(reverse('checkout:iniciar'))
        self.checkout = Checkout.objects.get(pk=self.client.session['checkout_atual'])
        self.assertRedirects(response, self.url('endereco'))
        return response

    def preparar(self):
        self.iniciar()
        self.client.post(self.url('endereco'), {'endereco': self.endereco.pk})
        self.client.post(self.url('entrega'), {'modalidade': 'PADRAO'})
        self.checkout.refresh_from_db()

    def confirmar(self):
        self.preparar()
        self.assertEqual(Pedido.objects.count(), 0)
        response = self.client.post(self.url('confirmar'))
        self.assertRedirects(response, self.url('pagamento'))
        self.checkout.refresh_from_db()
        return self.checkout.pedido

    def cartao(self, numero='4242 4242 4242 4242', **extra):
        hoje = timezone.localdate()
        dados = {'numero': numero, 'nome': 'Pessoa Fictícia',
                 'validade': f'{hoje.month:02d}/{(hoje.year + 2) % 100:02d}',
                 'cvv': '123', 'parcelas': 1}
        return dados | extra

    def test_fluxo_cartao_aprovado_congela_valores_e_conclui_uma_vez(self):
        pedido = self.confirmar()
        self.assertEqual(pedido.total, Decimal('100.00') + pedido.frete)
        self.assertEqual(pedido.prazo_entrega_dias, 7)
        self.assertEqual(pedido.endereco_dados['numero'], '10')
        response = self.client.post(self.url('cartao'), self.cartao(), follow=True)
        self.assertContains(response, 'Pagamento aprovado (simulação)')
        self.assertFalse(self.carrinho.itens.exists())
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.estoque, 8)
        self.checkout.refresh_from_db()
        self.assertTrue(self.checkout.estoque_baixado)

        # Atualizar, reabrir etapas e reenviar não duplica nem baixa novamente.
        for nome in ('resultado', 'pagamento', 'endereco', 'entrega'):
            self.assertEqual(self.client.get(self.url(nome), follow=True).status_code, 200)
        self.client.post(self.url('confirmar'))
        self.client.post(self.url('cartao'), self.cartao())
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(Pagamento.objects.count(), 1)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.estoque, 8)

        Produto.objects.filter(pk=self.livro.pk).update(preco=Decimal('99.00'))
        pedido.refresh_from_db()
        self.assertEqual(pedido.itens.get().preco_unitario, Decimal('50.00'))
        self.assertContains(self.client.get(self.url('resultado')), '100,00')

    def test_recusa_preserva_carrinho_e_permite_nova_tentativa_no_mesmo_pedido(self):
        pedido = self.confirmar()
        response = self.client.post(self.url('cartao'), self.cartao('4111 1111 1111 1111'), follow=True)
        self.assertContains(response, 'Pagamento recusado')
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, Pedido.Status.PAGAMENTO_RECUSADO)
        self.assertEqual(self.carrinho.itens.get().quantidade, 2)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.estoque, 10)
        self.client.post(self.url('cartao'), self.cartao())
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, Pedido.Status.PAGAMENTO_APROVADO)
        self.assertEqual(Pedido.objects.count(), 1)

    def test_pix_pendente_qr_nao_pagavel_e_confirmacao_explicita(self):
        pedido = self.confirmar()
        response = self.client.post(self.url('gerar_pix'), follow=True)
        self.assertContains(response, 'Pedido aguardando pagamento')
        self.assertContains(response, 'data:image/svg+xml;base64,')
        self.assertContains(response, 'PIX SIMULADO')
        pix = Pagamento.objects.get()
        self.assertIn('NAO PAGAVEL', pix.pix.conteudo_qr)
        self.assertEqual(self.carrinho.itens.get().quantidade, 2)
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        self.client.get(self.url('resultado'))
        self.client.post(self.url('gerar_pix'))
        self.assertEqual(Pagamento.objects.count(), 1)

        response = self.client.post(self.url('confirmar_pix', pix.pk), follow=True)
        self.assertContains(response, 'Pagamento aprovado (simulação)')
        self.assertFalse(self.carrinho.itens.exists())
        self.client.post(self.url('confirmar_pix', pix.pk))
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.estoque, 8)

    def test_pix_cancelado_ou_expirado_nao_aprova_e_pode_ser_regenerado(self):
        pedido = self.confirmar()
        self.client.post(self.url('gerar_pix'))
        pix = Pagamento.objects.get()
        self.client.post(self.url('cancelar_pix', pix.pk))
        pix.refresh_from_db()
        self.assertEqual(pix.status, Pagamento.Status.CANCELADO)
        self.client.post(self.url('gerar_pix'))
        novo = pedido.pagamentos.latest('pk')
        PagamentoPix.objects.filter(pagamento=novo).update(expira_em=timezone.now() - timedelta(seconds=1))
        response = self.client.post(self.url('confirmar_pix', novo.pk), follow=True)
        self.assertContains(response, 'expirou')
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        self.assertEqual(self.carrinho.itens.get().quantidade, 2)
        self.client.post(self.url('gerar_pix'))
        self.assertEqual(pedido.pagamentos.filter(status=Pagamento.Status.PENDENTE).count(), 1)

    def test_cotacao_nao_muda_ao_atualizar_voltar_ou_reenviar(self):
        self.preparar()
        cotacoes = self.checkout.cotacoes
        with patch('shipping.services.cotar_frete', side_effect=AssertionError('Não recotar')):
            self.client.get(self.url('entrega'))
            self.client.get(self.url('pagamento'))
            self.client.post(self.url('endereco'), {'endereco': self.endereco.pk})
            self.client.post(self.url('entrega'), {'modalidade': 'PADRAO', 'valor': '0.01', 'prazo_dias': 0})
            self.client.post(self.url('confirmar'), {'frete': '0.01', 'total': '0.01'})
            self.client.post(self.url('confirmar'))
        self.checkout.refresh_from_db()
        self.assertEqual(self.checkout.cotacoes, cotacoes)
        self.assertEqual(self.checkout.pedido.frete, Decimal(cotacoes['PADRAO']['valor']))
        self.assertEqual(Pedido.objects.count(), 1)

    def test_endereco_ausente_alheio_e_modalidade_invalida(self):
        self.iniciar()
        self.assertContains(self.client.post(self.url('endereco')), 'Selecione um endereço de entrega')
        self.assertContains(self.client.post(self.url('endereco'), {'endereco': self.endereco_alheio.pk}),
                            'Selecione um dos seus endereços')
        self.client.post(self.url('confirmar'))
        self.assertEqual(Pedido.objects.count(), 0)
        self.client.post(self.url('endereco'), {'endereco': self.endereco.pk})
        self.assertContains(self.client.post(self.url('entrega'), {'modalidade': 'AGENDADA'}),
                            'Selecione uma das modalidades cotadas')

    def test_carrinho_vazio_estoque_invalido_e_botao_bloqueado(self):
        Produto.objects.filter(pk=self.livro.pk).update(estoque=1)
        response = self.client.get(reverse('cart:detail'))
        self.assertContains(response, 'disabled>Finalizar compra')
        response = self.client.post(reverse('checkout:iniciar'), follow=True)
        self.assertContains(response, 'Estoque insuficiente')
        self.assertFalse(Checkout.objects.exists())
        self.carrinho.itens.all().delete()
        self.assertContains(self.client.post(reverse('checkout:iniciar'), follow=True), 'carrinho está vazio')

    def test_mudanca_de_preco_ou_quantidade_exige_revisao_antes_de_criar(self):
        for campo, valor in [('preco', Decimal('60.00')), ('estoque', 1)]:
            with self.subTest(campo=campo):
                Produto.objects.filter(pk=self.livro.pk).update(preco=Decimal('50.00'), estoque=10)
                self.preparar()
                Produto.objects.filter(pk=self.livro.pk).update(**{campo: valor})
                response = self.client.post(self.url('confirmar'), follow=True)
                self.assertContains(response, 'carrinho')
                self.assertEqual(Pedido.objects.count(), 0)
        Produto.objects.filter(pk=self.livro.pk).update(estoque=10)
        self.preparar()
        self.item.alterar_quantidade(3)
        self.client.post(self.url('confirmar'))
        self.assertEqual(Pedido.objects.count(), 0)

    def test_endereco_editado_ou_excluido_exige_nova_selecao(self):
        self.preparar()
        Endereco.objects.filter(pk=self.endereco.pk).update(numero='99')
        self.assertContains(self.client.post(self.url('confirmar'), follow=True), 'endereço mudou')
        self.assertEqual(Pedido.objects.count(), 0)
        self.client.post(self.url('endereco'), {'endereco': self.endereco.pk})
        self.client.post(self.url('entrega'), {'modalidade': 'PADRAO'})
        Endereco.objects.filter(pk=self.endereco.pk).delete()
        self.client.post(self.url('confirmar'))
        self.assertEqual(Pedido.objects.count(), 0)

    def test_estoque_esgota_apos_confirmacao_impede_aprovacao_de_cartao_e_pix(self):
        pedido = self.confirmar()
        self.client.post(self.url('gerar_pix'))
        pix = Pagamento.objects.get()
        Produto.objects.filter(pk=self.livro.pk).update(estoque=1)
        response = self.client.post(self.url('confirmar_pix', pix.pk), follow=True)
        self.assertContains(response, 'Estoque insuficiente')
        response = self.client.post(self.url('cartao'), self.cartao())
        self.assertContains(response, 'Estoque insuficiente')
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        self.assertFalse(pedido.pagamentos.filter(status=Pagamento.Status.APROVADO).exists())
        self.assertEqual(self.carrinho.itens.get().quantidade, 2)

    def test_itens_novos_e_quantidades_adicionais_nao_sao_apagados(self):
        self.confirmar()
        self.item.alterar_quantidade(3)
        eletronico = self.criar_eletronico()
        self.carrinho.adicionar(eletronico, 1)
        self.client.post(self.url('cartao'), self.cartao())
        self.assertEqual(self.carrinho.itens.get(produto=self.livro).quantidade, 1)
        self.assertEqual(self.carrinho.itens.get(produto=eletronico).quantidade, 1)

    def test_cartao_invalido_mostra_erros_sem_registrar_dados_sensiveis(self):
        self.confirmar()
        response = self.client.post(self.url('cartao'), self.cartao(numero='123', cvv='x'))
        self.assertContains(response, '16 dígitos')
        self.assertNotContains(response, 'value="x"')
        self.assertFalse(Pagamento.objects.exists())
        self.assertNotIn('cvv', str(self.client.session.items()))

    def test_rotas_exigem_dono_login_metodo_e_csrf(self):
        self.confirmar()
        self.client.post(self.url('gerar_pix'))
        pix = Pagamento.objects.get()
        self.client.force_login(self.outro)
        for nome in ('endereco', 'entrega', 'pagamento', 'resultado'):
            self.assertEqual(self.client.get(self.url(nome)).status_code, 404)
        for nome, extra in [('confirmar', []), ('cartao', []), ('gerar_pix', []),
                            ('confirmar_pix', [pix.pk]), ('cancelar_pix', [pix.pk])]:
            self.assertEqual(self.client.post(self.url(nome, *extra)).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.post(reverse('checkout:iniciar')).status_code, 302)
        self.assertEqual(self.client.get(self.url('resultado')).status_code, 302)
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(self.url('confirmar')).status_code, 405)
        seguro = Client(enforce_csrf_checks=True)
        seguro.force_login(self.usuario)
        self.assertEqual(seguro.post(reverse('checkout:iniciar')).status_code, 403)

    def test_formularios_reais_com_csrf_usam_rotas_do_checkout(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.usuario)

        def enviar(response, action, dados=None):
            forms = FormulariosHTML(response.content.decode()).formularios
            form = next(f for f in forms if f['atributos'].get('action', '') == action)
            return self.client.post(action or response.request['PATH_INFO'],
                                    form['campos'] | (dados or {}), follow=True)

        response = self.client.get(reverse('cart:detail'))
        response = enviar(response, reverse('checkout:iniciar'))
        self.checkout = Checkout.objects.get()
        response = enviar(response, '', {'endereco': self.endereco.pk})
        response = enviar(response, '', {'modalidade': 'EXPRESSA'})
        response = enviar(response, self.url('confirmar'))
        response = enviar(response, self.url('cartao'), self.cartao())
        self.assertContains(response, 'Pagamento aprovado (simulação)')
        self.assertEqual(Pedido.objects.get().tipo_entrega, 'EXPRESSA')

    def test_rotas_antigas_de_pagamento_reencaminham_compras_do_checkout(self):
        pedido = self.confirmar()
        self.assertRedirects(self.client.get(reverse('payments:pagar', args=[pedido.pk])), self.url('pagamento'))
        self.client.post(reverse('payments:pagar', args=[pedido.pk]), self.cartao())
        self.client.post(reverse('payments:gerar_pix', args=[pedido.pk]))
        self.assertFalse(Pagamento.objects.exists())
        self.client.post(self.url('gerar_pix'))
        pix = Pagamento.objects.get()
        self.client.post(reverse('payments:confirmar_pix', args=[pix.pk]))
        self.client.post(reverse('payments:cancelar_pix', args=[pix.pk]))
        pix.refresh_from_db()
        self.assertEqual(pix.status, Pagamento.Status.PENDENTE)

    def test_reenvio_do_inicio_reutiliza_mesma_intencao(self):
        self.iniciar()
        self.client.post(reverse('checkout:iniciar'))
        self.assertEqual(Checkout.objects.count(), 1)
        self.preparar()
        self.client.post(self.url('confirmar'))
        self.client.post(reverse('checkout:iniciar'))
        self.assertEqual(Checkout.objects.count(), 1)
        self.assertEqual(Pedido.objects.count(), 1)

    def test_falha_ao_baixar_estoque_desfaz_pagamento_e_historico(self):
        pedido = self.confirmar()
        from django.core.exceptions import ValidationError
        with patch('checkout.services._concluir', side_effect=ValidationError('Falha simulada na baixa.')):
            response = self.client.post(self.url('cartao'), self.cartao())
        self.assertContains(response, 'Falha simulada na baixa')
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        self.assertEqual(pedido.historico.count(), 1)
        self.assertFalse(Pagamento.objects.exists())
        self.assertEqual(self.carrinho.itens.get().quantidade, 2)

    def test_duas_compras_disputam_estoque_sem_aprovar_a_segunda(self):
        primeiro = self.confirmar()
        self.client.force_login(self.outro)
        Carrinho.do_usuario(self.outro).adicionar(self.livro, 2)
        self.iniciar()
        self.client.post(self.url('endereco'), {'endereco': self.endereco_alheio.pk})
        self.client.post(self.url('entrega'), {'modalidade': 'PADRAO'})
        self.client.post(self.url('confirmar'))
        segundo = Checkout.objects.get(pk=self.checkout.pk).pedido
        Produto.objects.filter(pk=self.livro.pk).update(estoque=3)
        primeiro_checkout = primeiro.checkout
        self.client.force_login(self.usuario)
        self.client.post(reverse('checkout:cartao', args=[primeiro_checkout.pk]), self.cartao())
        self.client.force_login(self.outro)
        response = self.client.post(self.url('cartao'), self.cartao())
        self.assertContains(response, 'Estoque insuficiente')
        segundo.refresh_from_db()
        self.assertEqual(segundo.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.estoque, 1)

    def test_trocar_pix_por_cartao_cancela_pix_e_conclui_mesmo_pedido(self):
        self.confirmar()
        self.client.post(self.url('gerar_pix'))
        pix = Pagamento.objects.get()
        response = self.client.get(self.url('pagamento'), {'metodo': 'cartao'})
        self.assertContains(response, f'action="{self.url("cartao")}"')
        self.client.post(self.url('cartao'), self.cartao())
        pix.refresh_from_db()
        self.assertEqual(pix.status, Pagamento.Status.CANCELADO)
        self.assertEqual(Pedido.objects.count(), 1)
