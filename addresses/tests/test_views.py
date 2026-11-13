from unittest.mock import patch
from urllib.error import URLError

from django.test import TestCase
from django.urls import reverse

from ..forms import SelecaoEnderecoForm
from ..models import Endereco
from .helpers import VIACEP_SE, criar_endereco, criar_usuario, dados_endereco, resposta_viacep

URLOPEN = 'addresses.viacep.urlopen'


class EnderecoViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = criar_usuario('ana')
        cls.bruno = criar_usuario('bruno')

    def setUp(self):
        self.client.force_login(self.ana)

    def post_novo(self, url=None, follow=False, **extra):
        return self.client.post(url or reverse('addresses:novo'), dados_endereco(**extra), follow=follow)

    def test_anonimo_e_redirecionado_ao_login(self):
        self.client.logout()
        for url in (reverse('addresses:lista'), reverse('addresses:novo')):
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 302)
                self.assertIn(reverse('login'), resposta['Location'])

    def test_lista_mostra_so_os_proprios_enderecos(self):
        criar_endereco(self.ana, logradouro='Rua da Ana')
        criar_endereco(self.bruno, logradouro='Rua do Bruno')
        resposta = self.client.get(reverse('addresses:lista'))
        self.assertContains(resposta, 'Rua da Ana')
        self.assertNotContains(resposta, 'Rua do Bruno')

    def test_lista_vazia(self):
        resposta = self.client.get(reverse('addresses:lista'))
        self.assertContains(resposta, 'Você ainda não cadastrou endereços')

    def test_cadastro_valido(self):
        resposta = self.post_novo(cep='01001000', padrao='on')
        self.assertRedirects(resposta, reverse('addresses:lista'))
        endereco = Endereco.objects.get(usuario=self.ana)
        self.assertEqual(endereco.cep, '01001-000')
        self.assertTrue(endereco.padrao)

    def test_cadastro_sem_numero_mantem_dados_e_mostra_erro(self):
        resposta = self.post_novo(numero='', logradouro='Rua Mantida')
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('numero', resposta.context['form'].errors)
        self.assertContains(resposta, 'Rua Mantida')
        self.assertFalse(Endereco.objects.exists())

    def test_cadastro_com_cep_invalido(self):
        resposta = self.post_novo(cep='12-34')
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('cep', resposta.context['form'].errors)
        self.assertFalse(Endereco.objects.exists())

    def test_editar_proprio_endereco(self):
        endereco = criar_endereco(self.ana)
        url = reverse('addresses:editar', args=[endereco.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        resposta = self.client.post(url, dados_endereco(numero='999', complemento='Fundos'))
        self.assertRedirects(resposta, reverse('addresses:lista'))
        endereco.refresh_from_db()
        self.assertEqual((endereco.numero, endereco.complemento), ('999', 'Fundos'))

    def test_excluir_e_tornar_padrao_no_proprio_endereco(self):
        primeiro = criar_endereco(self.ana, padrao=True)
        segundo = criar_endereco(self.ana, numero='200')

        resposta = self.client.post(reverse('addresses:tornar_padrao', args=[segundo.pk]))
        self.assertRedirects(resposta, reverse('addresses:lista'))
        primeiro.refresh_from_db()
        segundo.refresh_from_db()
        self.assertFalse(primeiro.padrao)
        self.assertTrue(segundo.padrao)

        resposta = self.client.post(reverse('addresses:excluir', args=[segundo.pk]), follow=True)
        self.assertFalse(Endereco.objects.filter(pk=segundo.pk).exists())
        mensagens = [str(m) for m in resposta.context['messages']]
        self.assertEqual(
            mensagens,
            ['Endereço excluído. Seu endereço padrão agora é Praça da Sé, 100.'],
        )
        self.assertEqual(Endereco.padrao_do_usuario(self.ana), primeiro)

        resposta = self.client.post(reverse('addresses:excluir', args=[primeiro.pk]), follow=True)
        self.assertEqual([str(m) for m in resposta.context['messages']], ['Endereço excluído.'])
        self.assertFalse(Endereco.objects.filter(usuario=self.ana).exists())

    def test_primeiro_cadastro_vira_padrao_com_aviso(self):
        resposta = self.post_novo(follow=True)
        self.assertEqual(
            [str(m) for m in resposta.context['messages']],
            ['Endereço cadastrado com sucesso e definido como seu endereço padrão.'],
        )
        self.assertTrue(Endereco.objects.get(usuario=self.ana).padrao)

        resposta = self.post_novo(numero='200', follow=True)
        self.assertEqual([str(m) for m in resposta.context['messages']], ['Endereço cadastrado com sucesso.'])
        self.assertFalse(Endereco.objects.get(usuario=self.ana, numero='200').padrao)

    def test_endereco_de_outro_usuario_retorna_404(self):
        criar_endereco(self.bruno, numero='50')  # vira o padrão do Bruno
        do_bruno = criar_endereco(self.bruno)
        acoes = [
            ('get', reverse('addresses:editar', args=[do_bruno.pk])),
            ('post', reverse('addresses:editar', args=[do_bruno.pk])),
            ('post', reverse('addresses:excluir', args=[do_bruno.pk])),
            ('post', reverse('addresses:tornar_padrao', args=[do_bruno.pk])),
        ]
        for metodo, url in acoes:
            with self.subTest(metodo=metodo, url=url):
                resposta = getattr(self.client, metodo)(url, dados_endereco(numero='1'))
                self.assertEqual(resposta.status_code, 404)
        do_bruno.refresh_from_db()
        self.assertEqual(do_bruno.numero, '100')
        self.assertFalse(do_bruno.padrao)

    def test_rotas_de_alteracao_exigem_post(self):
        endereco = criar_endereco(self.ana)
        for nome in ('addresses:excluir', 'addresses:tornar_padrao'):
            with self.subTest(rota=nome):
                self.assertEqual(self.client.get(reverse(nome, args=[endereco.pk])).status_code, 405)
        self.assertTrue(Endereco.objects.filter(pk=endereco.pk).exists())

    def test_next_seguro_e_preservado_e_externo_e_ignorado(self):
        url_seguro = reverse('addresses:novo') + '?next=/carrinho/'
        resposta = self.post_novo(url=url_seguro)
        self.assertRedirects(resposta, '/carrinho/', fetch_redirect_response=False)

        url_externo = reverse('addresses:novo') + '?next=https://exemplo.com/roubo'
        resposta = self.post_novo(url=url_externo, numero='2')
        self.assertRedirects(resposta, reverse('addresses:lista'))

    def test_post_invalido_preserva_next_no_formulario_e_no_cancelar(self):
        resposta = self.client.post(
            reverse('addresses:novo'), {**dados_endereco(numero=''), 'next': '/carrinho/'}
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, '<input type="hidden" name="next" value="/carrinho/">', html=True)
        self.assertEqual(resposta.context['cancelar_url'], '/carrinho/')

        resposta = self.client.post(
            reverse('addresses:novo'), {**dados_endereco(numero=''), 'next': 'https://exemplo.com/'}
        )
        self.assertEqual(resposta.context['next'], '')
        self.assertEqual(resposta.context['cancelar_url'], reverse('addresses:lista'))
        self.assertNotContains(resposta, 'exemplo.com')

    def test_link_meus_enderecos_no_menu_so_para_usuario_logado(self):
        link = f'href="{reverse("addresses:lista")}"'
        self.assertContains(self.client.get(reverse('catalog:index')), link)
        self.client.logout()
        self.assertNotContains(self.client.get(reverse('catalog:index')), link)

    def test_get_com_next_mostra_cancelar_para_o_destino(self):
        resposta = self.client.get(reverse('addresses:novo') + '?next=/carrinho/')
        self.assertContains(resposta, 'href="/carrinho/"')


class ConsultaCepEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = criar_usuario('ana')

    def setUp(self):
        self.client.force_login(self.ana)

    def url(self, cep):
        return reverse('addresses:consultar_cep', args=[cep])

    @patch(URLOPEN)
    def test_respostas_do_endpoint(self, urlopen):
        urlopen.return_value = resposta_viacep(VIACEP_SE)
        resposta = self.client.get(self.url('01001000'))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()['cidade'], 'São Paulo')
        self.assertEqual(resposta.json()['estado'], 'SP')

        self.assertEqual(self.client.get(self.url('123')).status_code, 400)

        urlopen.return_value = resposta_viacep({'erro': 'true'})
        resposta = self.client.get(self.url('99999999'))
        self.assertEqual(resposta.status_code, 404)
        self.assertIn('CEP não encontrado', resposta.json()['erro'])

        urlopen.side_effect = URLError('fora do ar')
        resposta = self.client.get(self.url('01001000'))
        self.assertEqual(resposta.status_code, 503)
        self.assertIn('indisponível', resposta.json()['erro'])

    def test_endpoint_exige_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url('01001000')).status_code, 302)

    @patch(URLOPEN, side_effect=URLError('fora do ar'))
    def test_falha_do_viacep_permite_preenchimento_manual(self, urlopen):
        self.assertEqual(self.client.get(self.url('01001000')).status_code, 503)

        resposta = self.client.post(reverse('addresses:novo'), dados_endereco(
            cep='01001000', logradouro='Rua Digitada', bairro='Bairro Digitado',
            cidade='Cidade Digitada', estado='MG',
        ))
        self.assertRedirects(resposta, reverse('addresses:lista'))
        endereco = Endereco.objects.get(usuario=self.ana)
        self.assertEqual(endereco.cep, '01001-000')
        self.assertEqual(endereco.logradouro, 'Rua Digitada')
        self.assertEqual(urlopen.call_count, 1)  # salvar não consulta o ViaCEP de novo


class SelecaoEnderecoFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = criar_usuario('ana')
        cls.bruno = criar_usuario('bruno')
        cls.da_ana = criar_endereco(cls.ana, numero='1')
        cls.padrao_da_ana = criar_endereco(cls.ana, numero='2', padrao=True)
        cls.do_bruno = criar_endereco(cls.bruno, numero='3')

    def test_lista_so_enderecos_do_usuario_com_padrao_inicial(self):
        form = SelecaoEnderecoForm(self.ana)
        self.assertEqual(
            set(form.fields['endereco'].queryset),
            {self.da_ana, self.padrao_da_ana},
        )
        self.assertEqual(form.initial['endereco'], self.padrao_da_ana.pk)

    def test_aceita_endereco_proprio_e_rejeita_alheio(self):
        form = SelecaoEnderecoForm(self.ana, data={'endereco': self.da_ana.pk})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['endereco'], self.da_ana)

        form = SelecaoEnderecoForm(self.ana, data={'endereco': self.do_bruno.pk})
        self.assertFalse(form.is_valid())
        self.assertIn('endereco', form.errors)

    def test_partial_de_selecao_renderiza(self):
        from django.template.loader import render_to_string
        html = render_to_string('addresses/_selecao.html', {
            'form': SelecaoEnderecoForm(self.ana), 'next_url': '/carrinho/',
        })
        self.assertIn('(padrão)', html)
        self.assertIn('next=/carrinho/', html)
        self.assertNotIn(', 3 ', html)
