"""Consulta de CEP no ViaCEP (https://viacep.com.br), única integração externa.

Usa apenas a biblioteca padrão (urllib). Os testes simulam `urlopen`, sem
depender da internet.
"""

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.exceptions import ValidationError

from .cep import MENSAGEM_CEP_INVALIDO, normalizar_cep

URL_VIACEP = 'https://viacep.com.br/ws/{cep}/json/'
TIMEOUT_SEGUNDOS = 5

ROTULOS_CAMPOS = {
    'logradouro': 'logradouro',
    'bairro': 'bairro',
    'cidade': 'cidade',
    'estado': 'estado (UF)',
}


class ErroConsultaCep(Exception):
    mensagem_padrao = 'Não foi possível obter os dados do endereço.'

    def __init__(self, mensagem=None):
        super().__init__(mensagem or self.mensagem_padrao)


class CepInvalido(ErroConsultaCep):
    mensagem_padrao = MENSAGEM_CEP_INVALIDO


class CepNaoEncontrado(ErroConsultaCep):
    mensagem_padrao = (
        'CEP não encontrado. Verifique o número informado e tente novamente, '
        'ou preencha o endereço manualmente.'
    )


class ServicoCepIndisponivel(ErroConsultaCep):
    mensagem_padrao = (
        'O serviço de consulta de CEP está indisponível no momento. Tente '
        'novamente mais tarde ou preencha os campos manualmente.'
    )


@dataclass(frozen=True)
class ResultadoCep:
    cep: str
    logradouro: str
    bairro: str
    cidade: str
    estado: str

    @property
    def campos_faltando(self):
        """Campos que o ViaCEP não retornou (ex.: CEP geral de cidade)."""
        return [campo for campo in ROTULOS_CAMPOS if not getattr(self, campo)]


def _texto(dados, chave):
    valor = dados.get(chave)
    return valor.strip() if isinstance(valor, str) else ''


def consultar_cep(cep):
    """Consulta o CEP e devolve um ResultadoCep.

    Levanta CepInvalido (sem acessar a rede), CepNaoEncontrado ou
    ServicoCepIndisponivel.
    """
    try:
        cep_normalizado = normalizar_cep(cep)
    except ValidationError:
        raise CepInvalido() from None

    requisicao = Request(
        URL_VIACEP.format(cep=cep_normalizado.replace('-', '')),
        headers={'Accept': 'application/json', 'User-Agent': 'AmazonAcademico/1.0'},
    )
    try:
        with urlopen(requisicao, timeout=TIMEOUT_SEGUNDOS) as resposta:
            dados = json.loads(resposta.read().decode('utf-8'))
    except HTTPError as erro:
        if erro.code == 400:
            raise CepInvalido() from None
        raise ServicoCepIndisponivel() from None
    except (URLError, TimeoutError, OSError):
        raise ServicoCepIndisponivel() from None
    except (ValueError, UnicodeDecodeError):
        # Resposta que não é JSON válido.
        raise ServicoCepIndisponivel() from None

    if not isinstance(dados, dict):
        raise ServicoCepIndisponivel()
    # O ViaCEP sinaliza CEP inexistente com {"erro": true} ou {"erro": "true"}.
    if str(dados.get('erro', '')).lower() == 'true':
        raise CepNaoEncontrado()

    from .models import Endereco  # import local evita ciclo na carga dos apps

    estado = _texto(dados, 'uf').upper()
    if estado not in Endereco.UF.values:
        estado = ''

    return ResultadoCep(
        cep=cep_normalizado,
        logradouro=_texto(dados, 'logradouro'),
        bairro=_texto(dados, 'bairro'),
        cidade=_texto(dados, 'localidade'),  # ViaCEP: localidade -> cidade
        estado=estado,                        # ViaCEP: uf -> estado
    )
