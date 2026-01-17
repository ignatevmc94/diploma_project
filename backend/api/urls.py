from django.urls import path
from .views import CartView, ImportProductsView, OrderListView, ProductListView, OrderConfirmView
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('import/', ImportProductsView.as_view()),
    path('products/', ProductListView.as_view()),
    path('token/', obtain_auth_token),
    path('cart/', CartView.as_view()),
    path('orders/', OrderListView.as_view()),
    path('order/confirm/', OrderConfirmView.as_view()),

]

