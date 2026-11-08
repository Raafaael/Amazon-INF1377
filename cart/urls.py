from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.detail, name='detail'),
    path('adicionar/<int:produto_id>/', views.add, name='add'),
    path('item/<int:item_id>/atualizar/', views.update, name='update'),
    path('item/<int:item_id>/remover/', views.remove, name='remove'),
]
