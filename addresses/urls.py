from django.urls import path

from . import views

app_name = 'addresses'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:endereco_id>/editar/', views.editar, name='editar'),
    path('<int:endereco_id>/excluir/', views.excluir, name='excluir'),
    path('<int:endereco_id>/padrao/', views.tornar_padrao, name='tornar_padrao'),
    path('cep/<str:cep>/', views.consultar_cep_view, name='consultar_cep'),
]
