from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cart.models import Carrinho
from catalog.tests.helpers import DadosCatalogoMixin
from orders.models import Pedido
from orders.services import criar_pedido

from payments import services
from payments.forms import CartaoForm
from payments.models import Pagamento, PagamentoPix

# Números fictícios válidos pelo algoritmo de Luhn; ambos podem aprovar ou recusar.
CARTAO_TESTE = '4242 4242 4242 4242'


def validade_futura():
    hoje = timezone.localdate()
    return f'{hoje.month:02d}/{(hoje.year + 2) % 100:02d}'


class PagamentosBase(DadosCatalogoMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.usuario = User.objects.create_user('cliente_pag', password='senha-teste-123')
        cls.outro = User.objects.create_user('outro_pag', password='senha-teste-123')

    def setUp(self):
        sorteio = patch('payments.services.secrets.randbelow', return_value=1)
        sorteio.start()
        self.addCleanup(sorteio.stop)
        self.livro = self.criar_livro()
        Carrinho.do_usuario(self.usuario).adicionar(self.livro, 2)
        self.pedido = criar_pedido(self.usuario, 'checkout-pag-1')

    def dados_cartao(self, numero=CARTAO_TESTE, **extra):
        dados = {'numero': numero, 'nome': 'Fulano Teste', 'validade': validade_futura(),
                 'cvv': '123', 'parcelas': 1}
        dados.update(extra)
        return dados

    def pagar(self, numero=CARTAO_TESTE, **extra):
        return services.pagar_com_cartao(self.usuario, self.pedido, **self.dados_cartao(numero, **extra))


class CartaoServicoTests(PagamentosBase):
    def test_cartao_aprovado_marca_pedido_como_pago(self):
        pagamento = self.pagar(CARTAO_TESTE, parcelas=3)
        self.pedido.refresh_from_db()
        self.assertEqual(pagamento.status, Pagamento.Status.APROVADO)
        self.assertEqual(pagamento.valor, self.pedido.total)
        self.assertEqual(self.pedido.status, Pedido.Status.PAGAMENTO_APROVADO)
        self.assertEqual(pagamento.cartao.ultimos_digitos, '4242')
        self.assertEqual(pagamento.cartao.parcelas, 3)
        self.assertEqual(pagamento.cartao.valor_parcela, Decimal('33.33'))
        self.assertEqual(self.pedido.historico.last().status, Pedido.Status.PAGAMENTO_APROVADO)

    def test_cartao_recusado_nao_marca_como_pago(self):
        with patch('payments.services.secrets.randbelow', return_value=0) as sorteio:
            pagamento = self.pagar(CARTAO_TESTE)
        sorteio.assert_called_once_with(2)
        self.pedido.refresh_from_db()
        self.assertEqual(pagamento.status, Pagamento.Status.RECUSADO)
        self.assertEqual(self.pedido.status, Pedido.Status.PAGAMENTO_RECUSADO)
        self.assertIn('Dados do cartão válidos', pagamento.mensagem)

    def test_nova_tentativa_apos_recusa(self):
        with patch('payments.services.secrets.randbelow', side_effect=[0, 1]) as sorteio:
            self.pagar(CARTAO_TESTE)
            self.pagar(CARTAO_TESTE)
        self.assertEqual(sorteio.call_count, 2)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.Status.PAGAMENTO_APROVADO)
        self.assertEqual(list(self.pedido.pagamentos.order_by('pk').values_list('status', flat=True)),
                         [Pagamento.Status.RECUSADO, Pagamento.Status.APROVADO])
        estados = list(self.pedido.historico.values_list('status', flat=True))
        self.assertEqual(estados, ['AGUARDANDO_PAGAMENTO', 'PAGAMENTO_RECUSADO',
                                   'AGUARDANDO_PAGAMENTO', 'PAGAMENTO_APROVADO'])

    def test_pedido_pago_nao_aceita_novo_pagamento(self):
        self.pagar()
        with self.assertRaises(ValidationError):
            self.pagar()
        with self.assertRaises(ValidationError):
            services.gerar_pix(self.usuario, self.pedido)
        self.assertEqual(Pagamento.objects.filter(status=Pagamento.Status.APROVADO).count(), 1)

    def test_dados_invalidos_nao_registram_pagamento(self):
        invalidos = [
            {'numero': '4242 4242 4242 4241'},             # Luhn
            {'numero': '4242 4242'},                        # curto
            {'validade': '13/30'},
            {'validade': '01/20'},                          # vencido
            {'cvv': '12'},
            {'nome': 'A1'},
            {'parcelas': 0},
            {'parcelas': 13},
        ]
        with patch('payments.services.secrets.randbelow', side_effect=AssertionError('Sorteio indevido')):
            for extra in invalidos:
                with self.subTest(extra=extra), self.assertRaises(ValidationError):
                    dados = self.dados_cartao(**extra)
                    services.pagar_com_cartao(self.usuario, self.pedido, **dados)
        self.assertFalse(Pagamento.objects.exists())

    def test_outro_usuario_nao_paga_pedido_alheio(self):
        with self.assertRaises(ValidationError):
            services.pagar_com_cartao(self.outro, self.pedido, **self.dados_cartao())

    def test_nao_persiste_numero_completo_nem_cvv(self):
        self.pagar()
        campos = {f.name for m in (Pagamento,) for f in m._meta.get_fields()}
        self.assertNotIn('cvv', campos)
        self.assertFalse(Pagamento.objects.filter(mensagem__contains='4242424242424242').exists())
        self.assertFalse(self.pedido.historico.filter(observacao__contains='4242424242424242').exists())

    def test_validade_mes_corrente_e_aceita(self):
        self.assertEqual(services.validar_validade('11/26', hoje=date(2026, 11, 30)), (11, 2026))
        with self.assertRaises(ValidationError):
            services.validar_validade('10/26', hoje=date(2026, 11, 1))


class PixServicoTests(PagamentosBase):
    def test_gerar_pix_fica_pendente_e_nao_paga_pedido(self):
        pagamento = services.gerar_pix(self.usuario, self.pedido)
        self.pedido.refresh_from_db()
        self.assertEqual(pagamento.status, Pagamento.Status.PENDENTE)
        self.assertEqual(self.pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        self.assertIn('PIX SIMULADO', pagamento.pix.conteudo_qr)
        self.assertFalse(pagamento.pix.conteudo_qr.startswith('000201'))  # não é BR Code
        self.assertAlmostEqual((pagamento.pix.expira_em - timezone.now()).total_seconds(), 60, delta=5)

    def test_gerar_pix_de_novo_reaproveita_o_pendente(self):
        primeiro = services.gerar_pix(self.usuario, self.pedido)
        self.assertEqual(services.gerar_pix(self.usuario, self.pedido), primeiro)

    def test_confirmar_pix_aprova(self):
        pagamento = services.gerar_pix(self.usuario, self.pedido)
        services.confirmar_pix(self.usuario, pagamento)
        self.pedido.refresh_from_db()
        pagamento.refresh_from_db()
        self.assertEqual(pagamento.status, Pagamento.Status.APROVADO)
        self.assertEqual(self.pedido.status, Pedido.Status.PAGAMENTO_APROVADO)

    def test_pix_expirado_nao_confirma_e_permite_gerar_outro(self):
        pagamento = services.gerar_pix(self.usuario, self.pedido)
        PagamentoPix.objects.filter(pk=pagamento.pk).update(expira_em=timezone.now() - timedelta(seconds=1))
        with self.assertRaises(ValidationError):
            services.confirmar_pix(self.usuario, pagamento)
        novo = services.gerar_pix(self.usuario, self.pedido)
        pagamento.refresh_from_db()
        self.assertNotEqual(novo.pk, pagamento.pk)
        self.assertEqual(pagamento.status, Pagamento.Status.CANCELADO)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)

    def test_cancelar_pix_mantem_pedido_aguardando(self):
        pagamento = services.gerar_pix(self.usuario, self.pedido)
        services.cancelar_pix(self.usuario, pagamento)
        pagamento.refresh_from_db()
        self.pedido.refresh_from_db()
        self.assertEqual(pagamento.status, Pagamento.Status.CANCELADO)
        self.assertEqual(self.pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        with self.assertRaises(ValidationError):
            services.confirmar_pix(self.usuario, pagamento)

    def test_cartao_cancela_pix_pendente(self):
        pix = services.gerar_pix(self.usuario, self.pedido)
        self.pagar()
        pix.refresh_from_db()
        self.assertEqual(pix.status, Pagamento.Status.CANCELADO)
        with self.assertRaises(ValidationError):
            services.confirmar_pix(self.usuario, pix)

    def test_outro_usuario_nao_confirma_pix_alheio(self):
        pagamento = services.gerar_pix(self.usuario, self.pedido)
        with self.assertRaises(ValidationError):
            services.confirmar_pix(self.outro, pagamento)


class FormularioTests(PagamentosBase):
    def test_form_limpa_mascara_e_nao_rerenderiza_cvv(self):
        form = CartaoForm(self.dados_cartao(), total=self.pedido.total)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['numero'], '4242424242424242')
        invalido = CartaoForm(self.dados_cartao(validade='99/99'), total=self.pedido.total)
        self.assertFalse(invalido.is_valid())
        self.assertNotIn('value="123"', invalido.as_p())


class ViewsTests(PagamentosBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.usuario)
        self.url = reverse('payments:pagar', args=[self.pedido.pk])

    def test_login_obrigatorio(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_pedido_de_outro_usuario_retorna_404(self):
        self.client.force_login(self.outro)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.post(self.url, self.dados_cartao()).status_code, 404)

    def test_pagina_mostra_aviso_de_simulacao_sem_revelar_regra(self):
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'Ambiente de simulação')
        for termo in ('final par', 'ímpar', 'paridade'):
            self.assertNotContains(resposta, termo)

    def test_post_cartao_aprovado(self):
        resposta = self.client.post(self.url, self.dados_cartao(), follow=True)
        self.assertContains(resposta, 'Pagamento aprovado')
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.Status.PAGAMENTO_APROVADO)

    def test_post_cartao_invalido_mostra_erro(self):
        resposta = self.client.post(self.url, self.dados_cartao(cvv='1'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'CVV deve ter 3 dígitos')
        self.assertFalse(Pagamento.objects.exists())

    def test_fluxo_pix_pela_interface(self):
        self.client.post(reverse('payments:gerar_pix', args=[self.pedido.pk]))
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'data:image/svg+xml;base64,')
        self.assertContains(resposta, 'Simular pagamento PIX')
        pix = Pagamento.objects.get()
        self.client.post(reverse('payments:confirmar_pix', args=[pix.pk]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.Status.PAGAMENTO_APROVADO)

    def test_pix_expirado_reabre_aba_pix_com_aviso(self):
        pix = services.gerar_pix(self.usuario, self.pedido)
        PagamentoPix.objects.filter(pk=pix.pk).update(expira_em=timezone.now() - timedelta(seconds=1))
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'Seu último PIX expirou')
        self.assertContains(resposta, 'Gerar novo PIX')
        self.assertContains(resposta, 'class="tab-pane fade show active" id="aba-pix"')
        with patch('payments.services.secrets.randbelow', return_value=0):
            self.pagar(CARTAO_TESTE)
        self.assertNotContains(self.client.get(self.url), 'Seu último PIX expirou')

    def test_erro_no_cartao_volta_na_aba_cartao_mesmo_com_pix_expirado(self):
        pix = services.gerar_pix(self.usuario, self.pedido)
        PagamentoPix.objects.filter(pk=pix.pk).update(expira_em=timezone.now() - timedelta(seconds=1))
        resposta = self.client.post(self.url, self.dados_cartao(validade='18/28'))
        self.assertContains(resposta, 'class="tab-pane fade show active" id="aba-cartao"')
        self.assertContains(resposta, 'Mês de validade inválido')

    def test_acoes_pix_exigem_post(self):
        pix = services.gerar_pix(self.usuario, self.pedido)
        self.assertEqual(self.client.get(reverse('payments:confirmar_pix', args=[pix.pk])).status_code, 405)

    def test_next_externo_e_ignorado(self):
        resposta = self.client.post(self.url, {**self.dados_cartao(), 'next': 'https://exemplo.com/'})
        self.assertEqual(resposta.url, self.url)

    def test_lista_mostra_apenas_pedidos_pagaveis_do_usuario(self):
        resposta = self.client.get(reverse('payments:lista'))
        self.assertContains(resposta, f'Pedido #{self.pedido.pk}')
        self.client.force_login(self.outro)
        self.assertNotContains(self.client.get(reverse('payments:lista')), f'Pedido #{self.pedido.pk}')
