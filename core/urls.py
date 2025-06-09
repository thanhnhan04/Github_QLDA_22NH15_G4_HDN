from django.urls import path
from .views import admin_home, admin_customer_support  # Ensure this matches the function name in views.py
from .views_pkg.auth_views import user_login, user_logout, register, profile  # Import từ core/views_pkg/auth_views.py
from .views_pkg.product_views import product_list, product_create, product_edit, product_delete  # Import từ core/views_pkg/product_views.py
from .views_pkg.cart_views import cart_detail, cart_add, cart_remove, cart_update_quantity  # Import từ core/views_pkg/cart_views.py
from .views_pkg.order_views import order_create, order_list, order_detail, order_confirm, ajax_promotion_calculate, mark_notification_read  # Import thêm mark_notification_read
from .views_pkg.admin_views import admin_products, admin_product_add, admin_product_edit, admin_product_delete, admin_product_toggle, admin_order_detail, admin_order_list, admin_order_update_status, admin_customers, admin_customer_toggle, admin_customer_detail, admin_statistics, admin_promotions, admin_promotion_add, admin_promotion_edit, admin_promotion_delete  # Import thêm các view mới
from . import views  # Import views for chat
urlpatterns = [
    # Authentication URLs
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),

    # Product URLs
    path('', product_list, name='home'),
    path('products/', product_list, name='product_list'),
    path('products/create/', product_create, name='product_create'),
    path('products/<int:pk>/edit/', product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),

    # Cart URLs
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', cart_update_quantity, name='cart_update_quantity'),

    # Order URLs
    path('orders/create/', order_create, name='order_create'),
    path('orders/', order_list, name='order_list'),
    path('orders/<int:pk>/', order_detail, name='order_detail'),
    path('orders/confirm/', order_confirm, name='order_confirm'),

    # Custom Admin Order Management
    path('admin-panel/orders/', admin_order_list, name='admin_order_list'),
    path('admin-panel/orders/<int:pk>/', admin_order_detail, name='admin_order_detail'),
    path('admin-panel/orders/<int:pk>/status/', admin_order_update_status, name='admin_order_update_status'),

    # Admin Home
    path('admin-home/', admin_home, name='admin_home'),
    
    # Admin Product Management
    path('admin_products/', admin_products, name='admin_products'),
    path('admin_products/add/', admin_product_add, name='admin_product_add'),
    path('admin_products/<int:pk>/edit/', admin_product_edit, name='admin_product_edit'),
    path('admin_products/<int:pk>/delete/', admin_product_delete, name='admin_product_delete'),
    path('admin_products/<int:pk>/toggle/', admin_product_toggle, name='admin_product_toggle'),    # Admin Statistics
    path('admin-statistics/', admin_statistics, name='admin_statistics'),
    path('admin-panel/statistics/', admin_statistics, name='admin_statistics'),
    
    # Admin Customer Management
    path('admin_customers/', admin_customers, name='admin_customers'),
    path('admin_customers/<int:pk>/toggle/', admin_customer_toggle, name='admin_customer_toggle'),
    path('admin_customers/<int:pk>/detail/', admin_customer_detail, name='admin_customer_detail'),

    # Admin Promotion Management
    path('admin-promotions/', admin_promotions, name='admin_promotions'),
    path('admin-promotions/add/', admin_promotion_add, name='admin_promotion_add'),
    path('admin-promotions/<int:pk>/edit/', admin_promotion_edit, name='admin_promotion_edit'),
    path('admin-promotions/<int:pk>/delete/', admin_promotion_delete, name='admin_promotion_delete'),

    # Ajax URLs
    path('ajax/promotion-calculate/', ajax_promotion_calculate, name='ajax_promotion_calculate'),

    # Notification URLs
    path('notifications/<int:pk>/read/', mark_notification_read, name='mark_notification_read'),
     # Chat URL
    path('chat/', views.chat, name='chat'),

    # Admin Customer Support
    path('admin-panel/customer-support/', admin_customer_support, name='admin_customer_support'),
]
