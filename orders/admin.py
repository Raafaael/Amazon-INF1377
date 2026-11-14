from django.contrib import admin

from .models import HistoricoStatusPedido, ItemPedido, Pedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    can_delete = False
    readonly_fields = ('produto', 'nome_produto', 'quantidade', 'preco_unitario', 'subtotal')


class HistoricoInline(admin.TabularInline):
    model = HistoricoStatusPedido
    extra = 0
    can_delete = False
    readonly_fields = ('status', 'data_alteracao', 'observacao')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'criado_em', 'status', 'total')
    list_filter = ('status',)
    search_fields = ('=id', 'usuario__username')
    inlines = (ItemPedidoInline, HistoricoInline)
    readonly_fields = ('usuario', 'criado_em', 'status', 'chave_checkout', 'subtotal_itens',
                       'frete', 'total', 'tipo_entrega', 'endereco_entrega', 'endereco_dados',
                       'prazo_entrega_dias', 'previsao_entrega', 'enviado_em', 'entregue_em')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
