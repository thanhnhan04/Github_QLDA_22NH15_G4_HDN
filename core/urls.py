from django.urls import path
from .views import auth_views, product_views, cart_views, order_views

urlpatterns = [
    # Authentication URLs
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
    path('profile/', auth_views.profile, name='profile'),

    # Product URLs
    path('', product_views.product_list, name='home'),
    path('products/', product_views.product_list, name='product_list'),
    path('products/create/', product_views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', product_views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', product_views.product_delete, name='product_delete'),

    # Cart URLs
    path('cart/', cart_views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', cart_views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', cart_views.cart_update_quantity, name='cart_update_quantity'),

    # Order URLs
    path('orders/create/', order_views.order_create, name='order_create'),
    path('orders/', order_views.order_list, name='order_list'),
    path('orders/<int:pk>/', order_views.order_detail, name='order_detail'),

    # Admin Order Management
    path('admin/orders/', order_views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:pk>/status/', order_views.admin_order_update_status, name='admin_order_update_status'),
]
