from django import forms
from django.core.exceptions import ValidationError

from . import services
from .models import MAX_PARCELAS


class CartaoForm(forms.Form):
    """Dados fictícios de cartão; o CVV nunca é re-renderizado nem salvo."""

    numero = forms.CharField(label='Número do cartão', max_length=19, widget=forms.TextInput(attrs={
        'inputmode': 'numeric', 'autocomplete': 'off', 'placeholder': '0000 0000 0000 0000',
        'data-mascara': 'cartao'}))
    nome = forms.CharField(label='Nome impresso no cartão', max_length=60, widget=forms.TextInput(attrs={
        'autocomplete': 'off', 'placeholder': 'NOME FICTÍCIO'}))
    validade = forms.CharField(label='Validade', max_length=5, widget=forms.TextInput(attrs={
        'inputmode': 'numeric', 'autocomplete': 'off', 'placeholder': 'MM/AA', 'data-mascara': 'validade'}))
    cvv = forms.CharField(label='CVV', max_length=3, widget=forms.PasswordInput(render_value=False, attrs={
        'inputmode': 'numeric', 'autocomplete': 'off', 'placeholder': '000', 'data-mascara': 'cvv'}))
    parcelas = forms.TypedChoiceField(label='Parcelas', coerce=int, initial=1)

    def __init__(self, *args, total, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parcelas'].choices = [
            (n, f'{n}x de R$ {services.valor_parcela(total, n):.2f} sem juros'.replace('.', ','))
            for n in range(1, MAX_PARCELAS + 1)
        ]
        for campo in self.fields.values():
            campo.widget.attrs.setdefault('class', 'form-select' if campo is self.fields['parcelas'] else 'form-control')

    def full_clean(self):
        super().full_clean()
        for nome in self.errors:
            if nome in self.fields:
                self.fields[nome].widget.attrs['class'] += ' is-invalid'

    def _validar(self, nome_campo, funcao):
        try:
            return funcao(self.cleaned_data.get(nome_campo, ''))
        except ValidationError as erro:
            raise forms.ValidationError(erro.messages)

    def clean_numero(self):
        return self._validar('numero', services.validar_numero_cartao)

    def clean_nome(self):
        return self._validar('nome', services.validar_nome)

    def clean_validade(self):
        self._validar('validade', services.validar_validade)
        return self.cleaned_data['validade'].strip()

    def clean_cvv(self):
        self._validar('cvv', services.validar_cvv)
        return self.cleaned_data['cvv'].strip()
