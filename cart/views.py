from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from catalog.models import Produto

from .models import Carrinho, ItemCarrinho


def _ler_quantidade(request):
    """Converte o campo `quantidade` do POST; devolve None se não for inteiro."""
    valor = (request.POST.get('quantidade') or '').strip()
    try:
        return int(valor)
    except ValueError:
        return None


@login_required
def detail(request):
    carrinho = Carrinho.do_usuario(request.user)
    return render(request, 'cart/detail.html', {
        'itens': carrinho.itens_com_produto(),
        'total': carrinho.total,
    })


@require_POST
def add(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    if not request.user.is_authenticated:
        messages.info(request, 'Entre na sua conta para adicionar produtos ao carrinho.')
        return redirect_to_login(reverse('catalog:product_detail', args=[produto.pk]))

    quantidade = _ler_quantidade(request)
    if quantidade is None:
        messages.error(request, 'A quantidade deve ser um número inteiro positivo.')
        return redirect('catalog:product_detail', produto_id=produto.pk)

    try:
        Carrinho.do_usuario(request.user).adicionar(produto, quantidade)
    except ValidationError as erro:
        messages.error(request, ' '.join(erro.messages))
        return redirect('catalog:product_detail', produto_id=produto.pk)

    messages.success(request, f'"{produto.nome}" foi adicionado ao carrinho.')
    return redirect('cart:detail')


@require_POST
@login_required
def update(request, item_id):
    item = get_object_or_404(ItemCarrinho.objects.select_related('produto'), pk=item_id, carrinho__usuario=request.user)
    quantidade = _ler_quantidade(request)
    if quantidade is None or quantidade < 0:
        messages.error(request, 'A quantidade deve ser um número inteiro positivo.')
        return redirect('cart:detail')

    nome = item.produto.nome
    try:
        resultado = item.alterar_quantidade(quantidade)
    except ValidationError as erro:
        messages.error(request, ' '.join(erro.messages))
        return redirect('cart:detail')

    if resultado is None:
        messages.success(request, f'"{nome}" foi removido do carrinho.')
    else:
        messages.success(request, f'Quantidade de "{nome}" atualizada.')
    return redirect('cart:detail')


@require_POST
@login_required
def remove(request, item_id):
    item = get_object_or_404(ItemCarrinho.objects.select_related('produto'), pk=item_id, carrinho__usuario=request.user)
    nome = item.produto.nome
    item.delete()
    messages.success(request, f'"{nome}" foi removido do carrinho.')
    return redirect('cart:detail')
