"""Dados de apoio para os testes de endereços (somente dados fictícios)."""

import json
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model

from ..models import Endereco


def criar_usuario(username):
    return get_user_model().objects.create_user(username, f'{username}@exemplo.com', 'senha-teste-123')


def dados_endereco(**extra):
    dados = {
        'cep': '01001-000',
        'logradouro': 'Praça da Sé',
        'numero': '100',
        'complemento': '',
        'bairro': 'Sé',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'tipo': Endereco.Tipo.CASA,
    }
    dados.update(extra)
    return dados


def criar_endereco(usuario, **extra):
    return Endereco.objects.create(usuario=usuario, **dados_endereco(**extra))


def resposta_viacep(dados):
    """Simula o objeto devolvido por urlopen() com o JSON informado."""
    resposta = MagicMock()
    corpo = dados if isinstance(dados, bytes) else json.dumps(dados).encode('utf-8')
    resposta.read.return_value = corpo
    resposta.__enter__.return_value = resposta
    return resposta


VIACEP_SE = {
    'cep': '01001-000',
    'logradouro': 'Praça da Sé',
    'complemento': 'lado ímpar',
    'bairro': 'Sé',
    'localidade': 'São Paulo',
    'uf': 'SP',
}
