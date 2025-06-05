print("core.views loaded")
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db import models
from .models import Product, Order, User  # Đảm bảo import đúng từ core.models

@staff_member_required
def admin_home(request):
    # Tổng số sản phẩm đang bán
    total_products = Product.objects.filter(is_available=True).count()

    # Tổng số đơn hàng
    total_orders = Order.objects.count()

    # Tổng doanh thu từ đơn hàng đã giao
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=models.Sum('total')
    )['total'] or 0

    # Tổng số khách hàng (không tính admin)
    total_users = User.objects.filter(role='customer').count()

    # Thông báo đơn hàng mới và đơn hàng vừa giao
    new_orders = Order.objects.filter(status='pending').order_by('-created_at')[:5]
    delivered_orders = Order.objects.filter(status='delivered').order_by('-updated_at')[:5]
    
    admin_notifications = []
    for order in new_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} vừa được đặt bởi {order.customer.username}.")
    for order in delivered_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} đã giao thành công.")

    return render(request, 'core/admin/admin_home.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'is_admin_page': True,
        'admin_notifications': admin_notifications,
    })
