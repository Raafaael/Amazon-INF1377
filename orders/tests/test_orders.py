from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from addresses.models import Endereco
from cart.models import Carrinho
from catalog.tests.helpers import DadosCatalogoMixin

from orders.models import HistoricoStatusPedido, Pedido
from orders.services import atualizar_status, criar_pedido


class PedidosBase(DadosCatalogoMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.usuario = User.objects.create_user('cliente_pedidos', password='senha-teste-123')
        cls.outro = User.objects.create_user('outro_pedidos', password='senha-teste-123')
        cls.staff = User.objects.create_user('admin_pedidos', password='senha-teste-123', is_staff=True)

    def setUp(self):
        self.livro = self.criar_livro()
        self.eletronico = self.criar_eletronico()

    def carrinho(self, usuario=None):
        return Carrinho.do_usuario(usuario or self.usuario)

    def pedido(self, chave='checkout-1', **kwargs):
        self.carrinho().adicionar(self.livro, 2)
        return criar_pedido(self.usuario, chave, **kwargs)

    def endereco(self, usuario=None):
        return Endereco.objects.create(
            usuario=usuario or self.usuario, cep='01001-000', logradouro='Rua Teste',
            numero='10', bairro='Centro', cidade='São Paulo', estado='SP', tipo='CASA',
        )


class CriacaoTests(PedidosBase):
    def test_cria_itens_total_e_historico_inicial_sem_baixar_estoque(self):
        self.carrinho().adicionar(self.livro, 2)
        self.carrinho().adicionar(self.eletronico, 1)
        endereco = self.endereco()
        pedido = criar_pedido(self.usuario, 'confirmacao-1', endereco=endereco,
                              frete=Decimal('15.50'), tipo_entrega='PADRAO', prazo_entrega_dias=5)
        self.assertEqual(pedido.subtotal_itens, Decimal('600.00'))
        self.assertEqual(pedido.total, Decimal('615.50'))
        self.assertEqual(pedido.status, Pedido.Status.AGUARDANDO_PAGAMENTO)
        self.assertEqual(pedido.itens.count(), 2)
        self.assertEqual(pedido.historico.count(), 1)
        self.assertEqual(pedido.endereco_dados, endereco.dados_para_pedido())
        self.assertEqual(self.livro.estoque, 3)
        self.assertEqual(self.carrinho().itens.count(), 2)

    def test_preco_nome_e_endereco_ficam_congelados(self):
        endereco = self.endereco()
        pedido = self.pedido(endereco=endereco, tipo_entrega='EXPRESSA')
        self.livro.nome = 'Livro renomeado'
        self.livro.preco = Decimal('90.00')
        self.livro.save()
        endereco.logradouro = 'Outra rua'
        endereco.save()
        item = pedido.itens.get()
        self.assertEqual((item.nome_produto, item.preco_unitario, item.subtotal),
                         ('Livro Teste', Decimal('50.00'), Decimal('100.00')))
        self.assertEqual(pedido.total, Decimal('100.00'))
        self.assertIn('Rua Teste', pedido.endereco_entrega)
        self.assertEqual(pedido.endereco_dados['logradouro'], 'Rua Teste')

    def test_reenvio_com_mesma_chave_nao_duplica_mesmo_com_carrinho_alterado(self):
        pedido = self.pedido()
        self.carrinho().itens.all().delete()
        self.assertEqual(criar_pedido(self.usuario, 'checkout-1').pk, pedido.pk)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(HistoricoStatusPedido.objects.count(), 1)

    def test_mesma_chave_outro_usuario_e_valida(self):
        self.pedido()
        self.carrinho(self.outro).adicionar(self.eletronico, 1)
        self.assertNotEqual(criar_pedido(self.outro, 'checkout-1').usuario_id, self.usuario.pk)

    def test_rejeita_carrinho_vazio_estoque_e_valores_invalidos(self):
        with self.assertRaisesMessage(ValidationError, 'carrinho está vazio'):
            criar_pedido(self.usuario, 'vazio')
        self.carrinho().adicionar(self.livro, 2)
        self.livro.estoque = 1
        self.livro.save()
        with self.assertRaisesMessage(ValidationError, 'Estoque insuficiente'):
            criar_pedido(self.usuario, 'sem-estoque')
        self.livro.estoque = 3
        self.livro.save()
        for frete in (Decimal('-1.00'), Decimal('NaN'), Decimal('1.001'), 1.0):
            with self.subTest(frete=frete), self.assertRaises(ValidationError):
                criar_pedido(self.usuario, 'valor-invalido', frete=frete, tipo_entrega='PADRAO', endereco=self.endereco())
        self.assertFalse(Pedido.objects.exists())

    def test_rejeita_endereco_alheio_e_entrega_sem_endereco(self):
        self.carrinho().adicionar(self.livro, 1)
        with self.assertRaisesMessage(ValidationError, 'pertencente ao cliente'):
            criar_pedido(self.usuario, 'alheio', endereco=self.endereco(self.outro))
        with self.assertRaisesMessage(ValidationError, 'Selecione um endereço'):
            criar_pedido(self.usuario, 'sem-endereco', tipo_entrega='PADRAO')

    def test_chave_obrigatoria(self):
        self.carrinho().adicionar(self.livro, 1)
        with self.assertRaises(ValidationError):
            criar_pedido(self.usuario, '')


class StatusTests(PedidosBase):
    def test_pagamento_aprovado_e_entrega_em_ordem(self):
        pedido = self.pedido()
        pedido = atualizar_status(pedido, Pedido.Status.PAGAMENTO_APROVADO, origem='pagamento')
        pedido = atualizar_status(pedido, Pedido.Status.EM_PREPARACAO, origem='entrega')
        pedido = atualizar_status(pedido, Pedido.Status.ENVIADO, origem='entrega')
        pedido = atualizar_status(pedido, Pedido.Status.ENTREGUE, origem='entrega')
        self.assertEqual(pedido.historico.count(), 5)
        self.assertLessEqual(pedido.enviado_em, pedido.entregue_em)
        self.assertEqual(list(pedido.historico.values_list('status', flat=True)), [
            Pedido.Status.AGUARDANDO_PAGAMENTO, Pedido.Status.PAGAMENTO_APROVADO,
            Pedido.Status.EM_PREPARACAO, Pedido.Status.ENVIADO, Pedido.Status.ENTREGUE,
        ])

    def test_bloqueia_salto_entrega_sem_pagamento_e_origem_inadequada(self):
        pedido = self.pedido()
        for status, origem in ((Pedido.Status.ENTREGUE, 'entrega'),
                               (Pedido.Status.EM_PREPARACAO, 'entrega'),
                               (Pedido.Status.PAGAMENTO_APROVADO, 'entrega'),
                               (Pedido.Status.PAGAMENTO_APROVADO, 'administracao')):
            with self.subTest(status=status, origem=origem), self.assertRaises(ValidationError):
                atualizar_status(pedido, status, origem=origem, usuario=self.staff)
        self.assertEqual(pedido.historico.count(), 1)

    def test_staff_pode_cancelar_cliente_nao_pode(self):
        pedido = self.pedido()
        with self.assertRaises(ValidationError):
            atualizar_status(pedido, Pedido.Status.CANCELADO, origem='administracao', usuario=self.usuario)
        pedido = atualizar_status(pedido, Pedido.Status.CANCELADO, origem='administracao', usuario=self.staff)
        self.assertEqual(pedido.status, Pedido.Status.CANCELADO)
        with self.assertRaises(ValidationError):
            atualizar_status(pedido, Pedido.Status.PAGAMENTO_APROVADO, origem='pagamento')

    def test_recusa_nao_e_aprovacao(self):
        pedido = self.pedido()
        pedido = atualizar_status(pedido, Pedido.Status.PAGAMENTO_RECUSADO, origem='pagamento')
        self.assertEqual(pedido.status, Pedido.Status.PAGAMENTO_RECUSADO)
        with self.assertRaises(ValidationError):
            atualizar_status(pedido, Pedido.Status.EM_PREPARACAO, origem='entrega')


class ConsultaTests(PedidosBase):
    def test_lista_e_detalhe_exigem_login(self):
        pedido = self.pedido()
        for url in (reverse('orders:lista'), reverse('orders:detalhe', args=[pedido.pk])):
            resposta = self.client.get(url)
            self.assertEqual(resposta.status_code, 302)
            self.assertIn('/accounts/login/', resposta.url)

    def test_lista_so_do_dono_mais_recente_primeiro(self):
        primeiro = self.pedido('primeiro')
        segundo = criar_pedido(self.usuario, 'segundo')
        self.carrinho(self.outro).adicionar(self.eletronico, 1)
        alheio = criar_pedido(self.outro, 'outro')
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse('orders:lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(list(resposta.context['pedidos']), [segundo, primeiro])
        self.assertNotContains(resposta, f'Pedido #{alheio.pk}')

    def test_detalhe_alheio_retorna_404_e_proprio_exibe_historico(self):
        pedido = self.pedido()
        self.client.force_login(self.outro)
        self.assertEqual(self.client.get(reverse('orders:detalhe', args=[pedido.pk])).status_code, 404)
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse('orders:detalhe', args=[pedido.pk]))
        self.assertContains(resposta, 'Livro Teste')
        self.assertContains(resposta, 'Aguardando pagamento')
        self.assertContains(resposta, 'Histórico de status')

    def test_resumo_do_detalhe_lista_itens_e_subtotal(self):
        self.carrinho().adicionar(self.livro, 2)
        self.carrinho().adicionar(self.eletronico, 1)
        pedido = criar_pedido(self.usuario, 'resumo-dois-itens')
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse('orders:detalhe', args=[pedido.pk]))
        self.assertContains(resposta, 'Produtos no resumo')
        self.assertContains(resposta, 'Subtotal dos itens')
        self.assertContains(resposta, 'Livro Teste', count=2)
        self.assertContains(resposta, 'Eletrônico Teste', count=2)

    def test_lista_e_detalhe_exibem_itens_ilustrados_com_link_ao_produto(self):
        pedido = self.pedido()
        self.livro.estoque = 0
        self.livro.save()
        self.client.force_login(self.usuario)
        link_produto = reverse('catalog:product_detail', args=[self.livro.pk])
        for url in (reverse('orders:lista'), reverse('orders:detalhe', args=[pedido.pk])):
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertContains(resposta, 'Livro Teste')
                self.assertContains(resposta, 'Imagem ilustrativa de Livro')
                self.assertContains(resposta, f'href="{link_produto}"')
        self.assertEqual(self.client.get(link_produto).status_code, 200)

    def test_estado_vazio(self):
        self.client.force_login(self.usuario)
        self.assertContains(self.client.get(reverse('orders:lista')), 'Você ainda não tem pedidos')


class DemonstracaoTests(PedidosBase):
    def test_comando_cria_pedido_do_carrinho_e_reexecucao_nao_duplica(self):
        self.carrinho().adicionar(self.livro, 1)
        saida = StringIO()
        call_command('criar_pedido_demo', self.usuario.username, stdout=saida)
        self.assertIn('Pedido #', saida.getvalue())
        self.assertEqual(Pedido.objects.get().total, Decimal('50.00'))
        self.carrinho().itens.all().delete()
        call_command('criar_pedido_demo', self.usuario.username, stdout=StringIO())
        self.assertEqual(Pedido.objects.count(), 1)

    def test_opcao_novo_cria_outra_intencao_com_os_itens_atuais(self):
        self.carrinho().adicionar(self.livro, 1)
        call_command('criar_pedido_demo', self.usuario.username, stdout=StringIO())
        self.carrinho().itens.all().delete()
        self.carrinho().adicionar(self.eletronico, 1)
        saida = StringIO()
        call_command('criar_pedido_demo', self.usuario.username, novo=True, stdout=saida)
        self.assertIn('(novo)', saida.getvalue())
        self.assertEqual(Pedido.objects.count(), 2)
        self.assertEqual(Pedido.objects.latest('pk').total, Decimal('500.00'))
