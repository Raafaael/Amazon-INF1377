from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Categoria, Fabricante, Produto

PRODUTOS_POR_PAGINA = 50


def _carregar_categorias():
    return Categoria.objects.filter(pai__isnull=True).prefetch_related('subcategorias').order_by('nome')


def _normalizar_valor_decimal(valor):
    if valor is None:
        return None
    texto = str(valor).strip().replace(',', '.')
    if not texto:
        return None
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None
    if not numero.is_finite():
        return None
    return numero


def _coletar_filtros(request):
    termo_busca = (request.GET.get('q') or '').strip()
    categoria_id = request.GET.get('categoria')
    fabricante_id = request.GET.get('fabricante')
    min_preco_raw = (request.GET.get('min_price') or '').strip()
    max_preco_raw = (request.GET.get('max_price') or '').strip()
    pagina = request.GET.get('page')

    categoria = None
    if categoria_id:
        categoria = get_object_or_404(Categoria, pk=categoria_id)

    fabricantes = Fabricante.objects.filter(eletronicos__isnull=False).distinct().order_by('nome')

    valores_validos = {}
    for nome, valor, label in (
        ('min_price', min_preco_raw, 'preço mínimo'),
        ('max_price', max_preco_raw, 'preço máximo'),
    ):
        if valor in (None, ''):
            valores_validos[nome] = None
            continue
        numero = _normalizar_valor_decimal(valor)
        if numero is None:
            messages.error(request, f'Valor inválido para {label}.')
            valores_validos[nome] = numero
            continue
        valores_validos[nome] = numero

    min_preco_valido = valores_validos['min_price']
    max_preco_valido = valores_validos['max_price']
    if min_preco_valido is not None and max_preco_valido is not None and min_preco_valido > max_preco_valido:
        messages.error(request, 'O preço mínimo não pode ser maior que o preço máximo.')
        min_preco_valido = None
        max_preco_valido = None

    queryset = Produto.objects.select_related(
        'categoria',
        'livro',
        'eletronico',
        'eletronico__fabricante',
        'livro__idioma',
        'livro__editora',
    ).prefetch_related('livro__autores').order_by('nome', 'id')

    if categoria is not None:
        queryset = queryset.filter(Q(categoria=categoria) | Q(categoria__pai=categoria))

    if termo_busca:
        queryset = queryset.filter(nome__icontains=termo_busca)

    if min_preco_valido is not None:
        queryset = queryset.filter(preco__gte=min_preco_valido)
    if max_preco_valido is not None:
        queryset = queryset.filter(preco__lte=max_preco_valido)

    if fabricante_id not in (None, '', '0'):
        fabricante = fabricantes.filter(pk=fabricante_id).first()
        if fabricante is None:
            messages.error(request, 'Fabricante selecionado não existe.')
        else:
            queryset = queryset.filter(eletronico__fabricante=fabricante)

    paginator = Paginator(queryset, PRODUTOS_POR_PAGINA)
    try:
        pagina_obj = paginator.page(pagina)
    except PageNotAnInteger:
        pagina_obj = paginator.page(1)
    except EmptyPage:
        pagina_obj = paginator.page(paginator.num_pages)

    return {
        'categorias': _carregar_categorias(),
        'categoria_selecionada': categoria,
        'fabricantes': fabricantes,
        'termo_busca': termo_busca,
        'min_preco': min_preco_raw,
        'max_preco': max_preco_raw,
        'min_preco_valido': min_preco_valido,
        'max_preco_valido': max_preco_valido,
        'fabricante_selecionado': int(fabricante_id) if fabricante_id and fabricante_id.isdigit() else '',
        'page_obj': pagina_obj,
        'total_produtos': paginator.count,
    }


def index(request):
    context = _coletar_filtros(request)
    return render(request, 'catalog/index.html', context)


def category(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    request.GET = request.GET.copy()
    request.GET['categoria'] = str(categoria.pk)
    context = _coletar_filtros(request)
    context['categoria_selecionada'] = categoria
    return render(request, 'catalog/index.html', context)


def product_detail(request, produto_id):
    produto = get_object_or_404(Produto.objects.select_related(
        'categoria',
        'livro',
        'eletronico',
        'eletronico__fabricante',
        'livro__idioma',
        'livro__editora',
    ).prefetch_related('livro__autores'), pk=produto_id)
    especializacao = produto.especializacao()
    return render(request, 'catalog/product_detail.html', {
        'produto': produto,
        'especializacao': especializacao,
        'categoria_selecionada': produto.categoria,
    })
