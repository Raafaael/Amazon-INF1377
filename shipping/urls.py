from django.urls import path

from . import views

app_name = 'shipping'

urlpatterns = [
    path('frete/', views.simulador, name='simulador'),
    path('pedidos/<int:pedido_id>/avancar/', views.avancar, name='avancar'),
]
