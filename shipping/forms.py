from django import forms
from django.core.exceptions import ValidationError

from addresses.cep import normalizar_cep


class CotacaoFreteForm(forms.Form):
    MODALIDADES = (
        ('PADRAO', 'Padrão'),
        ('EXPRESSA', 'Expressa'),
    )

    cep = forms.CharField(label='CEP', max_length=9)
    modalidade = forms.ChoiceField(label='Tipo de entrega', choices=MODALIDADES)

    def clean_cep(self):
        cep = self.cleaned_data['cep']
        try:
            return normalizar_cep(cep)
        except ValidationError as erro:
            raise forms.ValidationError(erro.messages[0]) from erro
