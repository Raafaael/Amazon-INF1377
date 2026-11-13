from django.contrib import admin

from .models import Endereco


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'logradouro', 'numero', 'cidade', 'estado', 'tipo', 'padrao')
    list_filter = ('estado', 'tipo', 'padrao')
    list_select_related = ('usuario',)
    search_fields = ('cep', 'cidade', 'logradouro', 'usuario__username')

    def delete_queryset(self, request, queryset):
        # Exclui um a um (com dados atualizados) para que Endereco.delete()
        # promova um novo padrão quando o padrão for excluído.
        for pk in list(queryset.values_list('pk', flat=True)):
            endereco = Endereco.objects.filter(pk=pk).first()
            if endereco:
                endereco.delete()
