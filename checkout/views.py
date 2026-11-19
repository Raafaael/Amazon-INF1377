from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from addresses.forms import SelecaoEnderecoForm
from payments.forms import CartaoForm
from payments.views import contexto_pagamento

from . import services
from .forms import EntregaForm
from .models import Checkout


def _obter(request, checkout_id):
    return get_object_or_404(Checkout.objects.select_related('pedido', 'endereco'),
                             pk=checkout_id, usuario=request.user)


def _url(nome, checkout):
    return reverse(f'checkout:{nome}', args=[checkout.pk])


def _erro(request, erro):
    messages.error(request, ' '.join(erro.messages))


def _render(request, checkout, etapa, **extra):
    pedido = checkout.pedido
    cotacao = checkout.cotacoes.get(checkout.modalidade)
    subtotal = (pedido.subtotal_itens if pedido else
                sum((Decimal(item['subtotal']) for item in checkout.resumo_carrinho), Decimal('0.00')))
    frete = pedido.frete if pedido else Decimal(cotacao['valor']) if cotacao else None
    contexto = {
        'checkout': checkout, 'pedido': pedido, 'etapa': etapa,
        'itens_resumo': list(pedido.itens.all()) if pedido else checkout.resumo_carrinho,
        'subtotal': subtotal, 'frete': frete,
        'total': subtotal + (frete or Decimal('0.00')),
        'etapas': [
            (1, 'Endereço', _url('endereco', checkout)),
            (2, 'Entrega', _url('entrega', checkout)),
            (3, 'Pagamento', _url('pagamento', checkout)),
            (4, 'Confirmação', _url('resultado', checkout) if pedido else ''),
        ],
        'cotacao': cotacao, 'next_url': _url('endereco', checkout),
    }
    if pedido:
        contexto.update(contexto_pagamento(pedido))
        pix = contexto['pix']
        contexto.update({
            'cartao_action': _url('cartao', checkout),
            'gerar_pix_action': _url('gerar_pix', checkout),
            'confirmar_pix_action': reverse('checkout:confirmar_pix', args=[checkout.pk, pix.pk]) if pix else '',
            'cancelar_pix_action': reverse('checkout:cancelar_pix', args=[checkout.pk, pix.pk]) if pix else '',
            'ultimo_pagamento': pedido.pagamentos.order_by('-criado_em', '-pk').first(),
        })
    contexto.update(extra)
    contexto['metodo'] = extra.get('metodo') or request.GET.get('metodo') or ('pix' if contexto.get('pix') else 'cartao')
    template = {1: 'endereco', 2: 'entrega', 3: 'pagamento', 4: 'resultado'}[etapa]
    response = render(request, f'checkout/{template}.html', contexto)
    response['Cache-Control'] = 'no-store'
    return response


@login_required
@require_http_methods(['GET', 'POST'])
def iniciar(request):
    # GET é útil após login; criar intenção exige o POST do carrinho com CSRF.
    if request.method == 'GET':
        return redirect('cart:detail')
    atual_id = request.session.get('checkout_atual')
    try:
        checkout = services.iniciar(request.user, atual_id)
    except ValidationError as erro:
        _erro(request, erro)
        return redirect('cart:detail')
    request.session['checkout_atual'] = str(checkout.pk)
    return redirect(_url('pagamento' if checkout.pedido_id else 'endereco', checkout))


@login_required
@require_http_methods(['GET', 'POST'])
def endereco(request, checkout_id):
    checkout = _obter(request, checkout_id)
    if checkout.pedido_id:
        return redirect(_url('pagamento', checkout))
    try:
        services.validar_carrinho(checkout)
    except ValidationError as erro:
        _erro(request, erro)
        return redirect('cart:detail')
    initial = {'endereco': checkout.endereco_id} if checkout.endereco_id else {}
    form = SelecaoEnderecoForm(request.user, request.POST if request.method == 'POST' else None,
                              initial=initial)
    if request.method == 'POST' and form.is_valid():
        try:
            services.selecionar_endereco(checkout, form.cleaned_data['endereco'])
        except ValidationError as erro:
            _erro(request, erro)
        else:
            return redirect(_url('entrega', checkout))
    return _render(request, checkout, 1, form=form)


@login_required
@require_http_methods(['GET', 'POST'])
def entrega(request, checkout_id):
    checkout = _obter(request, checkout_id)
    if checkout.pedido_id:
        return redirect(_url('pagamento', checkout))
    try:
        services.validar_carrinho(checkout)
        services.validar_endereco(checkout)
    except ValidationError as erro:
        _erro(request, erro)
        return redirect(_url('endereco', checkout))
    form = EntregaForm(request.POST if request.method == 'POST' else None,
                       cotacoes=checkout.cotacoes, initial={'modalidade': checkout.modalidade})
    if request.method == 'POST' and form.is_valid():
        try:
            services.selecionar_entrega(checkout, form.cleaned_data['modalidade'])
        except ValidationError as erro:
            _erro(request, erro)
        else:
            return redirect(_url('pagamento', checkout))
    return _render(request, checkout, 2, form=form)


@login_required
@require_GET
def pagamento(request, checkout_id):
    checkout = _obter(request, checkout_id)
    if checkout.estoque_baixado:
        return redirect(_url('resultado', checkout))
    if not checkout.pedido_id:
        try:
            services.validar_carrinho(checkout)
            services.validar_endereco(checkout)
        except ValidationError as erro:
            _erro(request, erro)
            return redirect(_url('endereco', checkout))
        if not checkout.modalidade:
            return redirect(_url('entrega', checkout))
    return _render(request, checkout, 3)


@login_required
@require_POST
def confirmar(request, checkout_id):
    checkout = _obter(request, checkout_id)
    try:
        services.confirmar_pedido(checkout)
    except ValidationError as erro:
        _erro(request, erro)
        return redirect(_url('endereco', checkout))
    return redirect(_url('pagamento', checkout))


@login_required
@require_POST
def cartao(request, checkout_id):
    checkout = _obter(request, checkout_id)
    if not checkout.pedido_id:
        return redirect(_url('pagamento', checkout))
    if checkout.estoque_baixado:
        return redirect(_url('resultado', checkout))
    form = CartaoForm(request.POST, total=checkout.pedido.total)
    if form.is_valid():
        try:
            services.pagar(checkout, 'CARTAO', form.cleaned_data)
        except ValidationError as erro:
            _erro(request, erro)
        else:
            return redirect(_url('resultado', checkout))
    return _render(request, checkout, 3, form_cartao=form, metodo='cartao')


@login_required
@require_POST
def gerar_pix(request, checkout_id):
    checkout = _obter(request, checkout_id)
    try:
        services.pagar(checkout, 'PIX')
    except ValidationError as erro:
        _erro(request, erro)
        return redirect(_url('pagamento', checkout))
    return redirect(_url('resultado', checkout))


def _acao_pix(request, checkout_id, pagamento_id, cancelar=False):
    checkout = _obter(request, checkout_id)
    try:
        services.acao_pix(checkout, pagamento_id, cancelar=cancelar)
    except ValidationError as erro:
        _erro(request, erro)
    return redirect(_url('resultado', checkout))


@login_required
@require_POST
def confirmar_pix(request, checkout_id, pagamento_id):
    return _acao_pix(request, checkout_id, pagamento_id)


@login_required
@require_POST
def cancelar_pix(request, checkout_id, pagamento_id):
    return _acao_pix(request, checkout_id, pagamento_id, cancelar=True)


@login_required
@require_GET
def resultado(request, checkout_id):
    checkout = _obter(request, checkout_id)
    if not checkout.pedido_id:
        return redirect(_url('pagamento', checkout))
    return _render(request, checkout, 4)
