from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from ..models import Product, Category, Order, OrderItem

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
    context = {'products': page_obj, 'categories': categories}
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
    context = {'orders': orders}
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