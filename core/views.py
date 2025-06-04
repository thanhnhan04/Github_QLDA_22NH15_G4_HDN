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
    return render(request, 'core/Admin/admin_home.html', {  # Đường dẫn template đã sửa để khớp với vị trí thực tế
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
    })
