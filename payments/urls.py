from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('pedido/<int:pedido_id>/', views.pagar, name='pagar'),
    path('pedido/<int:pedido_id>/pix/', views.gerar_pix, name='gerar_pix'),
    path('pix/<int:pagamento_id>/confirmar/', views.confirmar_pix, name='confirmar_pix'),
    path('pix/<int:pagamento_id>/cancelar/', views.cancelar_pix, name='cancelar_pix'),
]
