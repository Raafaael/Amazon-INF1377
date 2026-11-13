from django import forms

from .cep import normalizar_cep
from .models import Endereco


class EnderecoForm(forms.ModelForm):
    """Cadastro/edição de endereço (UC06). O usuário é definido pela view."""

    class Meta:
        model = Endereco
        fields = [
            'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'estado', 'tipo', 'padrao',
        ]
        labels = {
            'cep': 'CEP',
            'logradouro': 'Logradouro',
            'numero': 'Número',
            'complemento': 'Complemento (opcional)',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado (UF)',
            'tipo': 'Tipo de endereço',
            'padrao': 'Tornar este o meu endereço padrão',
        }
        widgets = {
            'cep': forms.TextInput(attrs={
                'inputmode': 'numeric',
                'maxlength': 9,
                'placeholder': '00000-000',
                'autocomplete': 'postal-code',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome, campo in self.fields.items():
            if nome == 'padrao':
                campo.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(campo.widget, forms.Select):
                campo.widget.attrs.setdefault('class', 'form-select')
            else:
                campo.widget.attrs.setdefault('class', 'form-control')

    def clean_cep(self):
        return normalizar_cep(self.cleaned_data['cep'])


class SelecaoEnderecoForm(forms.Form):
    """Escolha de um endereço do próprio usuário (para o checkout)."""

    endereco = forms.ModelChoiceField(
        queryset=Endereco.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None,
        label='Endereço de entrega',
        error_messages={
            'required': 'Selecione um endereço de entrega.',
            'invalid_choice': 'Selecione um dos seus endereços cadastrados.',
        },
    )

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enderecos = Endereco.do_usuario(usuario)
        campo = self.fields['endereco']
        campo.queryset = enderecos
        campo.label_from_instance = (
            lambda e: f'{e.texto_formatado}{" (padrão)" if e.padrao else ""}'
        )
        padrao = enderecos.filter(padrao=True).first()
        if padrao and 'endereco' not in self.initial:
            self.initial['endereco'] = padrao.pk
