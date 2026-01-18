from django.http import HttpResponse
from django.urls import path
from .views import (CartView, ImportProductsView, OrderListView, 
                    ProductListView, OrderCreateView, OrderConfirmView, 
                    RegisterView, LoginView, PasswordResetAPIView)
from django.contrib.auth import views as auth_views





urlpatterns = [
    path('import/', ImportProductsView.as_view()),
    path('products/', ProductListView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('password-reset/', PasswordResetAPIView.as_view()),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path('cart/', CartView.as_view()),
    path('orders/', OrderListView.as_view()),
    path('order/create/', OrderCreateView.as_view()),
    path('order/confirm/', OrderConfirmView.as_view()),

]

