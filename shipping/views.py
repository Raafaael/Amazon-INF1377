from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from orders.models import Pedido

from .forms import CotacaoFreteForm
from .services import avancar_entrega, cotar_frete


def simulador(request):
    cotacoes = []
    selecionada = None
    form = CotacaoFreteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dados = form.cleaned_data
        cep = dados['cep']
        modalidade = dados['modalidade']
        for tipo in ('PADRAO', 'EXPRESSA'):
            cotacao = cotar_frete(cep, tipo)
            cotacoes.append(cotacao)
        selecionada = next(
            (cotacao for cotacao in cotacoes if cotacao['tipo'] == modalidade),
            None,
        )

    return render(request, 'shipping/simulador.html', {
        'form': form,
        'cotacoes': cotacoes,
        'selecionada': selecionada,
    })


@require_POST
@staff_member_required
def avancar(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    try:
        avancar_entrega(pedido, request.user)
        messages.success(request, 'Entrega simulada avançada com sucesso.')
    except ValidationError as erro:
        messages.error(request, '; '.join(erro.messages))
    return redirect('orders:detalhe', pedido_id=pedido.pk)
