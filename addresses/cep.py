"""Normalização única do CEP, usada no formulário, no ViaCEP e na gravação."""

import re

from django.core.exceptions import ValidationError

_FORMATO_CEP = re.compile(r'^[0-9]{5}-?[0-9]{3}$')
MENSAGEM_CEP_INVALIDO = 'Informe um CEP válido no formato 00000-000.'


def normalizar_cep(valor):
    """Aceita '00000000' ou '00000-000' e devolve sempre '00000-000'.

    Qualquer outro formato gera ValidationError.
    """
    texto = (valor or '').strip()
    if not _FORMATO_CEP.match(texto):
        raise ValidationError(MENSAGEM_CEP_INVALIDO, code='cep_invalido')
    digitos = texto.replace('-', '')
    return f'{digitos[:5]}-{digitos[5:]}'


def validar_cep(valor):
    """Validador de campo: apenas confirma que o CEP pode ser normalizado."""
    normalizar_cep(valor)
