from django.contrib import admin

from .models import Pagamento, PagamentoCartao, PagamentoPix


class CartaoInline(admin.StackedInline):
    model = PagamentoCartao
    can_delete = False
    readonly_fields = ('bandeira', 'ultimos_digitos', 'parcelas', 'valor_parcela')


class PixInline(admin.StackedInline):
    model = PagamentoPix
    can_delete = False
    readonly_fields = ('codigo', 'expira_em')


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    """Somente leitura: resultados vêm do simulador, não de edição manual."""

    list_display = ('id', 'pedido', 'modalidade', 'valor', 'status', 'criado_em')
    list_filter = ('modalidade', 'status')
    search_fields = ('=id', '=pedido__id', 'pedido__usuario__username')
    inlines = (CartaoInline, PixInline)
    readonly_fields = ('pedido', 'modalidade', 'valor', 'status', 'mensagem', 'criado_em', 'atualizado_em')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
