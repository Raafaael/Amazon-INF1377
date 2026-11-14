from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<int:pedido_id>/', views.detalhe, name='detalhe'),
]
