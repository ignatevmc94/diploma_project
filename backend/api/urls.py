from django.urls import path
from .views import ImportProductsView


urlpatterns = [
    path('import/', ImportProductsView.as_view()),
]
