from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('categoria/<int:categoria_id>/', views.category, name='category'),
    path('produto/<int:produto_id>/', views.product_detail, name='product_detail'),
]
