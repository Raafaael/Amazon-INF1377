from django.urls import path

from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.iniciar, name='iniciar'),
    path('<uuid:checkout_id>/endereco/', views.endereco, name='endereco'),
    path('<uuid:checkout_id>/entrega/', views.entrega, name='entrega'),
    path('<uuid:checkout_id>/pagamento/', views.pagamento, name='pagamento'),
    path('<uuid:checkout_id>/confirmar/', views.confirmar, name='confirmar'),
    path('<uuid:checkout_id>/cartao/', views.cartao, name='cartao'),
    path('<uuid:checkout_id>/pix/', views.gerar_pix, name='gerar_pix'),
    path('<uuid:checkout_id>/pix/<int:pagamento_id>/confirmar/', views.confirmar_pix, name='confirmar_pix'),
    path('<uuid:checkout_id>/pix/<int:pagamento_id>/cancelar/', views.cancelar_pix, name='cancelar_pix'),
    path('<uuid:checkout_id>/resultado/', views.resultado, name='resultado'),
]
