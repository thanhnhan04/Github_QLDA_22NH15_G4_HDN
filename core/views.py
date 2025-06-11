print("core.views loaded")

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q  # Import Q for filtering
from .models import Product, Order, User, Message  # Ensure correct imports
from django.db import models

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

    # Thống kê sản phẩm: tất cả sản phẩm đang bán (tên, giá)
    product_stats = list(Product.objects.filter(is_available=True).values_list('name', 'price'))
    # Sản phẩm bán chạy nhất: top 5 theo số lượng đã bán (chỉ tính đơn hàng đã giao)
    from django.db.models import Sum, Q
    top_products = (
        Product.objects.annotate(
            sold=Sum('orderitem__quantity', filter=Q(orderitem__order__status='delivered'))
        )
        .filter(sold__gt=0)
        .order_by('-sold')[:5]
    )

    return render(request, 'core/admin/admin_home.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'is_admin_page': True,
        'admin_notifications': admin_notifications,
        'product_stats': product_stats,
        'top_products': top_products,
    })

@staff_member_required
def admin_customer_support(request):
    from django.contrib import messages  # Import messages framework
    admin_users = User.objects.filter(role='admin')

    # Lấy danh sách customer đã gửi tin nhắn đến bất kỳ admin nào
    customer_ids = Message.objects.filter(receiver__in=admin_users).values_list('sender', flat=True).distinct()
    customers = User.objects.filter(id__in=customer_ids)

    customer_id = request.GET.get('customer_id')
    selected_customer = None
    chat_messages = []  # Renamed to avoid conflict with Django messages framework

    if customer_id:
        try:
            selected_customer = User.objects.get(id=customer_id)
            # Lấy tất cả tin nhắn giữa selected_customer và bất kỳ admin nào
            chat_messages = Message.objects.filter(
                Q(sender=selected_customer, receiver__in=admin_users) |
                Q(sender__in=admin_users, receiver=selected_customer)
            ).order_by('timestamp')
        except User.DoesNotExist:
            selected_customer = None
            chat_messages = []

    # Xử lý gửi tin nhắn từ admin đến selected_customer
    if request.method == 'POST':
        customer_id_post = request.POST.get('customer_id')
        content = request.POST.get('content', '').strip()
        if customer_id_post and content:
            try:
                customer = User.objects.get(id=customer_id_post)
                Message.objects.create(sender=request.user, receiver=customer, content=content)
                messages.success(request, 'Tin nhắn đã được gửi thành công.')
            except User.DoesNotExist:
                messages.error(request, 'Không tìm thấy khách hàng.')
        return redirect(f"{request.path}?customer_id={customer_id_post}")

    return render(request, 'core/admin/customer_support.html', {
        'customers': customers,
        'selected_customer': selected_customer,
        'messages': messages,
        'is_customer_support_page': True,  # Add context for template identification
    })


@login_required
def chat(request):
    if request.user.role == 'admin':
        return redirect('admin_customer_support')

    # Get all admin users to track messages with any admin
    admin_users = User.objects.filter(role='admin')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content and admin_users.exists():
            # Send message to the first admin
            admin_user = admin_users.first()
            Message.objects.create(sender=request.user, receiver=admin_user, content=content)
        return redirect('chat')

    # Get messages between the customer and any admin
    messages = Message.objects.filter(
        Q(sender=request.user, receiver__in=admin_users) |  # Messages from customer to any admin
        Q(sender__in=admin_users, receiver=request.user)    # Messages from any admin to customer
    ).order_by('timestamp')

    return render(request, 'core/chat.html', {
        'messages': messages,
        'is_chat_page': True
    })

