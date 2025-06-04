from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from ..models import Order, OrderItem, Cart, User
from django import forms

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method', 'note']

@login_required
def order_create(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.items.exists():
        messages.error(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('cart_detail')

    cart_total = sum(item.price * item.quantity for item in cart.items.all())

    if request.method == 'POST':
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                customer=request.user,
                total=cart_total,
                status='pending',
                payment_method=request.POST.get('payment_method'),
                note=request.POST.get('note', '')
            )

            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product_name,
                    product_image_url=cart_item.product_image_url,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price,
                    total_price=cart_item.price * cart_item.quantity
                )            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, f'Đơn hàng #{order.id} đã được tạo thành công!')
            return redirect('order_detail', pk=order.id)

    return render(request, 'core/order/create.html', {
        'cart': cart,
        'total': cart_total,
        'payment_methods': Order.PAYMENT_CHOICES
    })

@login_required
def order_list(request):
    if request.user.role == 'admin':
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'core/order/list.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    if request.user.role == 'admin':
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, customer=request.user)
    return render(request, 'core/order/detail.html', {'order': order})

@user_passes_test(is_admin)
def admin_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'core/admin/order_list.html', {'orders': orders})

@user_passes_test(is_admin)
def admin_order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            status_text = dict(Order.STATUS_CHOICES)[new_status]
            messages.success(request, f'Đơn hàng #{order.id} đã được cập nhật thành {status_text}')
        else:
            messages.error(request, 'Trạng thái không hợp lệ')
    return redirect('admin_order_list')
