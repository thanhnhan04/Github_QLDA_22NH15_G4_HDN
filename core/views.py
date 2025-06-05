print("core.views loaded")
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db import models
from .models import Product, Order, User  # Đảm bảo import đúng từ core.models

@staff_member_required
def admin_home(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='completed').aggregate(total=models.Sum('total'))['total'] or 0
    total_users = User.objects.count()

    # Thông báo đơn hàng mới và đơn hàng vừa giao
    new_orders = Order.objects.filter(status='pending').order_by('-created_at')[:5]
    delivered_orders = Order.objects.filter(status='delivered').order_by('-updated_at')[:5]
    admin_notifications = []
    for order in new_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} vừa được đặt bởi {order.customer.username}.")
    for order in delivered_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} đã giao thành công.")

    return render(request, 'core/Admin/admin_home.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'is_admin_page': True,
        'admin_notifications': admin_notifications,
    })
