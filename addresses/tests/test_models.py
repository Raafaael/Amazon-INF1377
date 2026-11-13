from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

from ..cep import normalizar_cep
from ..models import Endereco
from .helpers import criar_endereco, criar_usuario, dados_endereco


class NormalizarCepTests(SimpleTestCase):
    def test_aceita_com_e_sem_hifen(self):
        self.assertEqual(normalizar_cep('01001000'), '01001-000')
        self.assertEqual(normalizar_cep(' 01001-000 '), '01001-000')

    def test_rejeita_formatos_invalidos(self):
        for valor in ('', '1234-567', '0100100', '010010000', 'abcde-fgh', '01001_000', '01.001-000'):
            with self.subTest(valor=valor):
                with self.assertRaises(ValidationError):
                    normalizar_cep(valor)


class EnderecoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = criar_usuario('ana')
        cls.bruno = criar_usuario('bruno')

    def test_save_normaliza_cep_mesmo_sem_full_clean(self):
        endereco = criar_endereco(self.ana, cep='01001000')
        endereco.refresh_from_db()
        self.assertEqual(endereco.cep, '01001-000')

    def test_save_rejeita_cep_invalido(self):
        with self.assertRaises(ValidationError):
            criar_endereco(self.ana, cep='123')
        self.assertFalse(Endereco.objects.exists())

    def test_numero_obrigatorio_e_complemento_opcional(self):
        sem_numero = Endereco(usuario=self.ana, **dados_endereco(numero=''))
        with self.assertRaises(ValidationError) as ctx:
            sem_numero.full_clean()
        self.assertIn('numero', ctx.exception.message_dict)

        sem_complemento = Endereco(usuario=self.ana, **dados_endereco(complemento=''))
        sem_complemento.full_clean()

    def test_campos_de_localizacao_obrigatorios(self):
        endereco = Endereco(usuario=self.ana, **dados_endereco(logradouro='', bairro='', cidade='', tipo=''))
        with self.assertRaises(ValidationError) as ctx:
            endereco.full_clean()
        for campo in ('logradouro', 'bairro', 'cidade', 'tipo'):
            self.assertIn(campo, ctx.exception.message_dict)

    def test_uf_invalida(self):
        endereco = Endereco(usuario=self.ana, **dados_endereco(estado='XX'))
        with self.assertRaises(ValidationError) as ctx:
            endereco.full_clean()
        self.assertIn('estado', ctx.exception.message_dict)

    def test_novo_padrao_desmarca_o_anterior_do_mesmo_usuario(self):
        antigo = criar_endereco(self.ana, padrao=True)
        do_bruno = criar_endereco(self.bruno, padrao=True)
        novo = criar_endereco(self.ana, numero='200', padrao=True)

        antigo.refresh_from_db()
        do_bruno.refresh_from_db()
        self.assertFalse(antigo.padrao)
        self.assertTrue(novo.padrao)
        self.assertTrue(do_bruno.padrao)
        self.assertEqual(Endereco.padrao_do_usuario(self.ana), novo)

    def test_primeiro_endereco_vira_padrao_e_os_seguintes_nao(self):
        primeiro = criar_endereco(self.ana)
        segundo = criar_endereco(self.ana, numero='200')
        self.assertTrue(primeiro.padrao)
        self.assertFalse(segundo.padrao)

    def test_cadastro_sem_padrao_existente_vira_padrao(self):
        unico = criar_endereco(self.ana)
        unico.delete()
        novo = criar_endereco(self.ana, numero='300')
        self.assertTrue(novo.padrao)

    def test_excluir_padrao_promove_o_mais_recente(self):
        padrao = criar_endereco(self.ana, numero='1')
        antigo = criar_endereco(self.ana, numero='2')
        recente = criar_endereco(self.ana, numero='3')
        do_bruno = criar_endereco(self.bruno)

        padrao.delete()
        self.assertEqual(padrao.novo_padrao, recente)
        self.assertEqual(Endereco.padrao_do_usuario(self.ana), recente)
        antigo.refresh_from_db()
        self.assertFalse(antigo.padrao)
        do_bruno.refresh_from_db()
        self.assertTrue(do_bruno.padrao)

    def test_excluir_nao_padrao_mantem_o_padrao(self):
        padrao = criar_endereco(self.ana, numero='1')
        outro = criar_endereco(self.ana, numero='2')
        outro.delete()
        self.assertIsNone(outro.novo_padrao)
        self.assertEqual(Endereco.padrao_do_usuario(self.ana), padrao)

    def test_definir_como_padrao(self):
        primeiro = criar_endereco(self.ana, padrao=True)
        segundo = criar_endereco(self.ana, numero='200')
        segundo.definir_como_padrao()
        primeiro.refresh_from_db()
        self.assertFalse(primeiro.padrao)
        self.assertEqual(Endereco.padrao_do_usuario(self.ana), segundo)

    def test_banco_impede_dois_padroes_do_mesmo_usuario(self):
        criar_endereco(self.ana, padrao=True)
        segundo = criar_endereco(self.ana, numero='200')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Endereco.objects.filter(pk=segundo.pk).update(padrao=True)

    def test_do_usuario_traz_so_os_proprios_com_padrao_primeiro(self):
        a1 = criar_endereco(self.ana, numero='1')
        a2 = criar_endereco(self.ana, numero='2', padrao=True)
        criar_endereco(self.bruno, numero='3')
        self.assertEqual(list(Endereco.do_usuario(self.ana)), [a2, a1])

    def test_obter_do_usuario_nao_retorna_endereco_alheio(self):
        do_bruno = criar_endereco(self.bruno)
        with self.assertRaises(Endereco.DoesNotExist):
            Endereco.obter_do_usuario(self.ana, do_bruno.pk)

    def test_dados_para_pedido_e_texto(self):
        endereco = criar_endereco(self.ana, complemento='Apto 12')
        self.assertEqual(endereco.dados_para_pedido(), {
            'cep': '01001-000',
            'logradouro': 'Praça da Sé',
            'numero': '100',
            'complemento': 'Apto 12',
            'bairro': 'Sé',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'tipo': 'CASA',
        })
        self.assertEqual(
            endereco.texto_formatado,
            'Praça da Sé, 100 - Apto 12 — Sé, São Paulo/SP — CEP 01001-000',
        )
