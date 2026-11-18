from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.tests.helpers import DadosCatalogoMixin
from orders.models import Pedido
from orders.services import atualizar_status

from .services import cotar_frete, avancar_entrega


class FreteTests(TestCase):
    @patch('shipping.services.randint', side_effect=[1200, 3500])
    def test_frete_aleatorio_respeita_limites_e_padrao_e_mais_barato(self, randint_mock):
        hoje = timezone.localdate()
        padrao = cotar_frete('01001-000', 'PADRAO', hoje=hoje)
        expressa = cotar_frete('01001-000', 'EXPRESSA', hoje=hoje)
        self.assertEqual(padrao['valor'], Decimal('12'))
        self.assertEqual(padrao['prazo_dias'], 7)
        self.assertEqual(expressa['valor'], Decimal('35'))
        self.assertEqual(expressa['prazo_dias'], 3)
        self.assertLess(padrao['valor'], expressa['valor'])
        self.assertEqual(randint_mock.call_args_list[0].args, (1200, 2000))
        self.assertEqual(randint_mock.call_args_list[1].args, (2500, 3500))

    def test_rejeita_modalidade_agendada_ou_desconhecida(self):
        hoje = timezone.localdate()
        for modalidade in ('AGENDADA', 'INEXISTENTE'):
            with self.subTest(modalidade=modalidade), self.assertRaises(ValidationError):
                cotar_frete('01001-000', modalidade, hoje=hoje)


class EntregaTests(DadosCatalogoMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.usuario = User.objects.create_user('cliente_entrega', password='senha-teste-123')
        cls.staff = User.objects.create_user('admin_entrega', password='senha-teste-123', is_staff=True)

    def criar_pedido(self):
        from cart.models import Carrinho
        livro = self.criar_livro()
        Carrinho.do_usuario(self.usuario).adicionar(livro, 1)
        from orders.services import criar_pedido
        return criar_pedido(self.usuario, 'entrega-teste')

    def test_avanca_apos_pagamento_sem_saltar_e_protege_cliente(self):
        pedido = self.criar_pedido()
        with self.assertRaises(ValidationError):
            avancar_entrega(pedido, self.usuario)

        pedido = atualizar_status(
            pedido,
            Pedido.Status.PAGAMENTO_APROVADO,
            origem='pagamento',
        )
        pedido = avancar_entrega(pedido, self.staff)
        self.assertEqual(pedido.status, Pedido.Status.EM_PREPARACAO)
        pedido = avancar_entrega(pedido, self.staff)
        self.assertEqual(pedido.status, Pedido.Status.ENVIADO)
        self.assertIsNotNone(pedido.enviado_em)
        pedido = avancar_entrega(pedido, self.staff)
        self.assertEqual(pedido.status, Pedido.Status.ENTREGUE)
        self.assertIsNotNone(pedido.entregue_em)
        with self.assertRaises(ValidationError):
            avancar_entrega(pedido, self.staff)

    def test_view_avanca_so_para_staff(self):
        pedido = self.criar_pedido()
        pedido = atualizar_status(pedido, Pedido.Status.PAGAMENTO_APROVADO, origem='pagamento')
        url = reverse('shipping:avancar', args=[pedido.pk])
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.client.force_login(self.staff)
        resposta = self.client.post(url)
        self.assertRedirects(
            resposta,
            reverse('orders:detalhe', args=[pedido.pk]),
            fetch_redirect_response=False,
        )
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, Pedido.Status.EM_PREPARACAO)

    def test_simulador_exibe_comparacao_e_validacao(self):
        url = reverse('shipping:simulador')
        resposta_inicial = self.client.get(url)
        self.assertNotContains(resposta_inicial, 'Agendada')
        self.assertNotIn('data_agendada', resposta_inicial.context['form'].fields)
        with patch('shipping.services.randint', side_effect=[1590, 2990]):
            resposta = self.client.post(url, {
                'cep': '01001-000',
                'modalidade': 'EXPRESSA',
            })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.context['cotacoes']), 2)
        self.assertContains(resposta, 'R$ 15,90')
        self.assertContains(resposta, 'R$ 29,90')
        resposta = self.client.post(url, {
            'cep': '01001-000',
            'modalidade': 'AGENDADA',
        })
        self.assertEqual(resposta.context['cotacoes'], [])
        resposta = self.client.post(reverse('shipping:simulador'), {
            'cep': 'invalido',
            'modalidade': 'PADRAO',
        })
        self.assertContains(resposta, 'CEP válido')
