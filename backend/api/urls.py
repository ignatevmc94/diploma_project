from django.urls import path
from .views import ImportProductsView, ProductListView


urlpatterns = [
    path('import/', ImportProductsView.as_view()),
    path('products/', ProductListView.as_view()),
]
