from django.urls import path
from .views import (CartView, ImportProductsView, OrderListView, 
                    ProductListView, OrderCreateView, OrderConfirmView, 
                    OrderView, RegisterView, LoginView, PasswordResetAPIView,
                    ContactView, ContactDetailView, CartItemDeleteView,
                    ProductDetailView, SupplierOrderListView,
                    SupplierAcceptionView, SupplierOrderStatusView)
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('import/', ImportProductsView.as_view()),
    path('products/', ProductListView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('password-reset/', PasswordResetAPIView.as_view()),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
    path('cart/', CartView.as_view()),
    path('cart/<int:item_id>/', CartItemDeleteView.as_view()),
    path('orders/', OrderListView.as_view()),
    path('order/create/', OrderCreateView.as_view()),
    path('order/confirm/', OrderConfirmView.as_view()),
    path('order/<int:pk>/', OrderView.as_view()),
    path('contacts/', ContactView.as_view()),
    path('contacts/<int:pk>/', ContactDetailView.as_view()),
    path('supplier/orders/', SupplierOrderListView.as_view()),
    path('supplier/orders/<int:pk>/status/', SupplierOrderStatusView.as_view()),
    path('supplier/acception/', SupplierAcceptionView.as_view()),
]

