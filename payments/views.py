import base64

import qrcode
import qrcode.image.svg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from orders.models import Pedido

from . import services
from .forms import CartaoForm
from .models import Pagamento


def _next_seguro(request):
    # Mesmo critério de addresses.views: aceita apenas destinos internos (ex.: checkout).
    destino = (request.POST.get('next') or request.GET.get('next') or '').strip()
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()},
                                                   require_https=request.is_secure()):
        return destino
    return ''


def qr_data_uri(texto):
    """QR Code gerado localmente em SVG (sem Pillow), pronto para <img src>."""
    svg = qrcode.make(texto, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2).to_string()
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg).decode('ascii')


def contexto_pagamento(pedido, form=None):
    """Contexto usado pelos partials `payments/_cartao.html` e `payments/_pix.html` (também no checkout)."""
    pix = services.pix_ativo(pedido)
    pix_expirado = not pix and services.ultimo_pix_expirou(pedido)
    return {
        'pedido': pedido,
        'pagavel': pedido.status in services.STATUS_PAGAVEIS,
        'form_cartao': form or CartaoForm(total=pedido.total),
        'pix': pix,
        'pix_expirado': pix_expirado,
        'aba_ativa': 'pix' if pix or pix_expirado else 'cartao',
        'pix_qr': qr_data_uri(pix.pix.conteudo_qr) if pix else '',
        'expiracao_segundos': int(services.EXPIRACAO_PIX.total_seconds()),
    }


def _pedido_do_usuario(request, pedido_id):
    return get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)


@login_required
def lista(request):
    pedidos = (Pedido.objects.filter(usuario=request.user, status__in=services.STATUS_PAGAVEIS)
               .order_by('-criado_em', '-id'))
    return render(request, 'payments/lista.html', {'pedidos': pedidos})


@login_required
def pagar(request, pedido_id):
    """Página de demonstração: cartão fictício (POST aqui) e PIX simulado."""
    pedido = _pedido_do_usuario(request, pedido_id)
    proximo = _next_seguro(request)
    form = None
    if request.method == 'POST':
        form = CartaoForm(request.POST, total=pedido.total)
        if form.is_valid():
            try:
                pagamento = services.pagar_com_cartao(request.user, pedido, **form.cleaned_data)
            except ValidationError as erro:
                messages.error(request, ' '.join(erro.messages))
            else:
                nivel = messages.success if pagamento.status == Pagamento.Status.APROVADO else messages.error
                nivel(request, f'{pagamento.mensagem} (simulação, sem cobrança real)')
                return redirect(proximo or reverse('payments:pagar', args=[pedido.pk]))
            form = None
        else:
            messages.error(request, 'Corrija os dados do cartão fictício.')
        pedido.refresh_from_db()
    contexto = contexto_pagamento(pedido, form)
    # Envio pelo cartão volta sempre na aba Cartão, para mostrar erros/resultado.
    contexto['aba_ativa'] = 'cartao' if request.method == 'POST' else contexto['aba_ativa']
    contexto['tentativas'] = pedido.pagamentos.select_related('cartao', 'pix')
    contexto['next'] = proximo
    return render(request, 'payments/pagar.html', contexto)


@require_POST
@login_required
def gerar_pix(request, pedido_id):
    pedido = _pedido_do_usuario(request, pedido_id)
    try:
        services.gerar_pix(request.user, pedido)
        messages.info(request, 'PIX simulado gerado. Ele não pode ser pago em um banco real.')
    except ValidationError as erro:
        messages.error(request, ' '.join(erro.messages))
    return redirect(_next_seguro(request) or reverse('payments:pagar', args=[pedido.pk]))


def _acao_pix(request, pagamento_id, acao, sucesso):
    pagamento = get_object_or_404(Pagamento, pk=pagamento_id, pedido__usuario=request.user,
                                  modalidade=Pagamento.Modalidade.PIX)
    try:
        acao(request.user, pagamento)
        messages.success(request, sucesso)
    except ValidationError as erro:
        messages.error(request, ' '.join(erro.messages))
    return redirect(_next_seguro(request) or reverse('payments:pagar', args=[pagamento.pedido_id]))


@require_POST
@login_required
def confirmar_pix(request, pagamento_id):
    return _acao_pix(request, pagamento_id, services.confirmar_pix,
                     'PIX simulado confirmado. Pedido marcado como pago (simulação).')


@require_POST
@login_required
def cancelar_pix(request, pagamento_id):
    return _acao_pix(request, pagamento_id, services.cancelar_pix,
                     'PIX simulado cancelado. O pedido continua aguardando pagamento.')
