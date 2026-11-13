from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from .forms import EnderecoForm
from .models import Endereco
from .viacep import CepInvalido, CepNaoEncontrado, ServicoCepIndisponivel, consultar_cep


def _next_seguro(request):
    """Destino de retorno (ex.: checkout) vindo de GET ou POST; descarta URLs externas."""
    destino = (request.POST.get('next') or request.GET.get('next') or '').strip()
    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destino
    return ''


def _renderizar_formulario(request, form, titulo, proximo, endereco=None):
    return render(request, 'addresses/form.html', {
        'form': form,
        'titulo': titulo,
        'endereco': endereco,
        'next': proximo,
        'cancelar_url': proximo or reverse('addresses:lista'),
    })


@login_required
def lista(request):
    return render(request, 'addresses/lista.html', {
        'enderecos': Endereco.do_usuario(request.user),
    })


@login_required
def novo(request):
    proximo = _next_seguro(request)
    if request.method == 'POST':
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco = form.save(commit=False)
            endereco.usuario = request.user
            marcado_pelo_usuario = endereco.padrao
            endereco.save()
            if endereco.padrao and not marcado_pelo_usuario:
                messages.success(request, 'Endereço cadastrado com sucesso e definido como seu endereço padrão.')
            else:
                messages.success(request, 'Endereço cadastrado com sucesso.')
            return redirect(proximo or 'addresses:lista')
        messages.error(request, 'Corrija os campos indicados para salvar o endereço.')
    else:
        form = EnderecoForm()
    return _renderizar_formulario(request, form, 'Novo endereço', proximo)


@login_required
def editar(request, endereco_id):
    endereco = get_object_or_404(Endereco, pk=endereco_id, usuario=request.user)
    proximo = _next_seguro(request)
    if request.method == 'POST':
        form = EnderecoForm(request.POST, instance=endereco)
        if form.is_valid():
            form.save()
            messages.success(request, 'Endereço atualizado com sucesso.')
            return redirect(proximo or 'addresses:lista')
        messages.error(request, 'Corrija os campos indicados para salvar o endereço.')
    else:
        form = EnderecoForm(instance=endereco)
    return _renderizar_formulario(request, form, 'Editar endereço', proximo, endereco)


@require_POST
@login_required
def excluir(request, endereco_id):
    endereco = get_object_or_404(Endereco, pk=endereco_id, usuario=request.user)
    era_padrao = endereco.padrao
    endereco.delete()
    mensagem = 'Endereço excluído.'
    if era_padrao and endereco.novo_padrao:
        novo = endereco.novo_padrao
        mensagem += f' Seu endereço padrão agora é {novo.logradouro}, {novo.numero}.'
    messages.success(request, mensagem)
    return redirect('addresses:lista')


@require_POST
@login_required
def tornar_padrao(request, endereco_id):
    endereco = get_object_or_404(Endereco, pk=endereco_id, usuario=request.user)
    endereco.definir_como_padrao()
    messages.success(request, 'Endereço padrão atualizado.')
    return redirect('addresses:lista')


@require_GET
@login_required
def consultar_cep_view(request, cep):
    """JSON usado pelo formulário para preencher os campos a partir do CEP."""
    try:
        resultado = consultar_cep(cep)
    except CepInvalido as erro:
        return JsonResponse({'erro': str(erro)}, status=400)
    except CepNaoEncontrado as erro:
        return JsonResponse({'erro': str(erro)}, status=404)
    except ServicoCepIndisponivel as erro:
        return JsonResponse({'erro': str(erro)}, status=503)
    return JsonResponse({
        'cep': resultado.cep,
        'logradouro': resultado.logradouro,
        'bairro': resultado.bairro,
        'cidade': resultado.cidade,
        'estado': resultado.estado,
        'campos_faltando': resultado.campos_faltando,
    })
