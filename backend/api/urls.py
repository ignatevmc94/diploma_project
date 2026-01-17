from django.urls import path
from .views import ImportProductsView, ProductListView
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('import/', ImportProductsView.as_view()),
    path('products/', ProductListView.as_view()),
    path('token/', obtain_auth_token,)
]
