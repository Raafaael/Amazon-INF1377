from django import forms


class EntregaForm(forms.Form):
    modalidade = forms.ChoiceField(
        label='Modalidade de entrega', widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Selecione uma modalidade de entrega.',
                        'invalid_choice': 'Selecione uma das modalidades cotadas.'},
    )

    def __init__(self, *args, cotacoes, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['modalidade'].choices = [
            (tipo, f'{"Padrão" if tipo == "PADRAO" else "Expressa"} — '
                   f'R$ {cotacao["valor"].replace(".", ",")} — '
                   f'{cotacao["prazo_dias"]} dias')
            for tipo, cotacao in cotacoes.items()
        ]
