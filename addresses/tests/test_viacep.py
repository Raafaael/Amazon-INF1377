from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.test import SimpleTestCase

from ..viacep import CepInvalido, CepNaoEncontrado, ServicoCepIndisponivel, consultar_cep
from .helpers import VIACEP_SE, resposta_viacep

URLOPEN = 'addresses.viacep.urlopen'


class ConsultarCepTests(SimpleTestCase):
    @patch(URLOPEN)
    def test_sucesso_mapeia_localidade_e_uf(self, urlopen):
        urlopen.return_value = resposta_viacep(VIACEP_SE)
        resultado = consultar_cep('01001000')
        self.assertEqual(resultado.cep, '01001-000')
        self.assertEqual(resultado.logradouro, 'Praça da Sé')
        self.assertEqual(resultado.bairro, 'Sé')
        self.assertEqual(resultado.cidade, 'São Paulo')
        self.assertEqual(resultado.estado, 'SP')
        self.assertEqual(resultado.campos_faltando, [])
        url = urlopen.call_args.args[0].full_url
        self.assertEqual(url, 'https://viacep.com.br/ws/01001000/json/')

    @patch(URLOPEN)
    def test_cep_inexistente_com_erro_booleano_ou_texto(self, urlopen):
        for corpo in ({'erro': True}, {'erro': 'true'}):
            with self.subTest(corpo=corpo):
                urlopen.return_value = resposta_viacep(corpo)
                with self.assertRaises(CepNaoEncontrado):
                    consultar_cep('99999-999')

    @patch(URLOPEN)
    def test_cep_invalido_nao_acessa_a_rede(self, urlopen):
        with self.assertRaises(CepInvalido):
            consultar_cep('123')
        urlopen.assert_not_called()

    @patch(URLOPEN)
    def test_falhas_de_rede_e_resposta_invalida(self, urlopen):
        falhas = [
            URLError('sem conexão'),
            TimeoutError('timeout'),
            HTTPError('https://viacep.com.br', 500, 'erro', None, None),
        ]
        for falha in falhas:
            with self.subTest(falha=type(falha).__name__):
                urlopen.side_effect = falha
                with self.assertRaises(ServicoCepIndisponivel):
                    consultar_cep('01001-000')

        urlopen.side_effect = None
        urlopen.return_value = resposta_viacep(b'<html>fora do ar</html>')
        with self.assertRaises(ServicoCepIndisponivel):
            consultar_cep('01001-000')

    @patch(URLOPEN)
    def test_resposta_incompleta_indica_campos_faltando(self, urlopen):
        urlopen.return_value = resposta_viacep({
            'cep': '13870-000', 'logradouro': '', 'bairro': '',
            'localidade': 'Cidade Exemplo', 'uf': 'SP',
        })
        resultado = consultar_cep('13870-000')
        self.assertEqual(resultado.cidade, 'Cidade Exemplo')
        self.assertEqual(resultado.campos_faltando, ['logradouro', 'bairro'])
