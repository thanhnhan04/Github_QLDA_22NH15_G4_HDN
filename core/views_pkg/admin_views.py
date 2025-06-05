from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from ..models import Product, Category, Order, OrderItem, User

@staff_member_required
def admin_products(request):
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-created_at')
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    availability = request.GET.get('available', '')
    if availability:
        is_available = (availability == 'True')
        products = products.filter(is_available=is_available)
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_products = Product.objects.count()

    # Thông báo đơn hàng mới và đơn hàng vừa giao
    from ..models import Order
    new_orders = Order.objects.filter(status='pending').order_by('-created_at')[:5]
    delivered_orders = Order.objects.filter(status='delivered').order_by('-updated_at')[:5]
    admin_notifications = []
    for order in new_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} vừa được đặt bởi {order.customer.username}.")
    for order in delivered_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} đã giao thành công.")

    context = {'products': page_obj, 'categories': categories, 'is_admin_page': True, 'total_products': total_products, 'admin_notifications': admin_notifications}
    return render(request, 'core/Admin/admin_products.html', context)

@staff_member_required
def admin_product_add(request):
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        description = request.POST.get('description', '')
        category_id = request.POST['category']
        is_available = 'is_available' in request.POST
        image = request.FILES.get('image')
        image_url = request.POST.get('image_url', '')  # Handle external image URL
        category = get_object_or_404(Category, id=category_id)
        product = Product(
            name=name,
            price=price,
            description=description,
            category=category,
            is_available=is_available,
            image_url=image_url  # Save the external image URL
        )
        if image:
            product.image = image
        product.save()
        messages.success(request, f'Product "{name}" added successfully.')
    return redirect('admin_products')

@staff_member_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        # Nếu chỉ upload ảnh từ form nhanh trên bảng
        if 'image_url' in request.FILES:
            # Xử lý upload file ảnh
            image_file = request.FILES['image_url']
            # Nếu model Product có trường image, lưu file vào đó
            if hasattr(product, 'image'):
                product.image = image_file
                # Nếu muốn lấy url, cần xử lý lưu file và lấy url nếu cần
            product.save()
            messages.success(request, f'Đã thêm ảnh cho sản phẩm "{product.name}".')
            return redirect('admin_products')
        # ...existing code...
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.description = request.POST.get('description', '')
        category_id = request.POST['category']
        product.is_available = 'is_available' in request.POST
        product.category = get_object_or_404(Category, id=category_id)
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.image_url = request.POST.get('image_url', '')  # Update external image URL
        product.save()
        messages.success(request, f'Product "{product.name}" updated successfully.')
        return redirect('admin_products')
    else:
        data = {
            'name': product.name,
            'price': str(product.price),
            'description': product.description,
            'category': product.category.id,
            'is_available': product.is_available,
            'image_url': product.image_url,  # Include external image URL
        }
        return JsonResponse(data)

@staff_member_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, f'Product "{product.name}" deleted successfully.')
    return redirect('admin_products')

@staff_member_required
def admin_product_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_available = not product.is_available
    product.save()
    status = "visible" if product.is_available else "hidden"
    messages.success(request, f'Product "{product.name}" is now {status}.')
    return redirect('admin_products')

@staff_member_required
def admin_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Thông báo đơn hàng mới và đơn hàng vừa giao
    new_orders = Order.objects.filter(status='pending').order_by('-created_at')[:5]
    delivered_orders = Order.objects.filter(status='delivered').order_by('-updated_at')[:5]
    admin_notifications = []
    for order in new_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} vừa được đặt bởi {order.customer.username}.")
    for order in delivered_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} đã giao thành công.")

    context = {'orders': orders, 'status_filter': status_filter, 'is_admin_page': True, 'admin_notifications': admin_notifications}
    return render(request, 'core/admin/order_list.html', context)  # Updated template path

@staff_member_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = OrderItem.objects.filter(order=order)
    context = {'order': order, 'order_items': order_items}
    return render(request, 'core/Admin/admin_order_detail.html', context)

@staff_member_required
def admin_order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to "{new_status}".')
    return redirect('admin_order_list')

@staff_member_required
def admin_customers(request):
    # Chỉ lấy các tài khoản customer, không lấy admin
    customers = User.objects.exclude(role='admin').order_by('-date_joined')
    # Tìm kiếm
    search = request.GET.get('search', '').strip()
    if search:
        customers = customers.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(username__icontains=search) |
            models.Q(email__icontains=search)
        )
    # Lọc trạng thái
    status = request.GET.get('status', '')
    if status == 'active':
        customers = customers.filter(is_active=True)
    elif status == 'inactive':
        customers = customers.filter(is_active=False)
    # Phân trang
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_customers = User.objects.filter(role='customer').count()

    # Thông báo đơn hàng mới và đơn hàng vừa giao
    new_orders = Order.objects.filter(status='pending').order_by('-created_at')[:5]
    delivered_orders = Order.objects.filter(status='delivered').order_by('-updated_at')[:5]
    admin_notifications = []
    for order in new_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} vừa được đặt bởi {order.customer.username}.")
    for order in delivered_orders:
        admin_notifications.append(f"Đơn hàng #{order.id} đã giao thành công.")

    context = {
        'customers': page_obj,
        'search': search,
        'status': status,
        'is_admin_page': True,
        'total_customers': total_customers,
        'admin_notifications': admin_notifications,
    }
    return render(request, 'core/admin/admin_customers.html', context)

@staff_member_required
def admin_customer_toggle(request, pk):
    user = get_object_or_404(User, pk=pk, role='customer')
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        if user.is_active:
            messages.success(request, f'Đã mở khóa khách hàng {user.username}')
        else:
            messages.warning(request, f'Đã chặn khách hàng {user.username}')
    return redirect('admin_customers')

@staff_member_required
def admin_customer_detail(request, pk):
    user = get_object_or_404(User, pk=pk, role='customer')
    orders = user.orders.all().order_by('-created_at')  # Sử dụng related_name='orders' từ model Order
    return render(request, 'core/admin/admin_customer_detail.html', {'customer': user, 'orders': orders})

@staff_member_required
def admin_statistics(request):
    # Basic statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total')
    )['total'] or 0    # Đếm số lượng tài khoản không phải admin
    total_users = User.objects.exclude(role='admin').count()

    # Orders by status with translated labels
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Top selling products - count items from delivered orders only
    top_products = Product.objects.annotate(
        sold=Count('orderitem', filter=Q(orderitem__order__status='delivered'))
    ).filter(sold__gt=0).order_by('-sold')[:5]
    
    # Daily sales data for the last 7 days
    today = timezone.now()
    last_week = today - timedelta(days=7)
    daily_sales = Order.objects.filter(
        created_at__gte=last_week,
        status='delivered'
    ).values('created_at__date').annotate(
        total=Sum('total')
    ).order_by('created_at__date')
    
    # Sales over time (last 7 days)
    today = timezone.now()
    last_week = today - timedelta(days=7)
    daily_sales = Order.objects.filter(
        created_at__gte=last_week,
        status='delivered'
    ).values('created_at__date').annotate(
        total=Sum('total')
    ).order_by('created_at__date')
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'orders_by_status': orders_by_status,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'daily_sales': daily_sales,
        'is_admin_page': True,
    }
    
    return render(request, 'core/admin/statistics.html', context)