from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Pedido


@login_required
def lista(request):
    pedidos = (Pedido.objects.filter(usuario=request.user)
               .prefetch_related('itens__produto')
               .order_by('-criado_em', '-id'))
    return render(request, 'orders/lista.html', {'pedidos': pedidos})


@login_required
def detalhe(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.filter(usuario=request.user).prefetch_related('itens__produto', 'historico'),
        pk=pedido_id,
    )
    return render(request, 'orders/detalhe.html', {'pedido': pedido})
