from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Cart, CartItem, Product
from django.db.models import F, Sum, DecimalField
from django.db.models.functions import Cast
from decimal import Decimal

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_total = Decimal('0.00')
    
    for item in cart.items.all():
        item.item_total = item.price * item.quantity
        cart_total += item.item_total
    
    return render(request, 'core/cart/detail.html', {
        'cart': cart,
        'cart_total': cart_total
    })

@login_required
def cart_add(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'product_name': product.name,
            'product_image_url': product.image_url,
            'price': product.price,
            'quantity': 1
        }
    )
    if not created:
        cart_item.quantity = F('quantity') + 1
        cart_item.save()
        cart_item.refresh_from_db()  # Refresh to get updated quantity
    
    messages.success(request, 'Đã thêm món vào giỏ hàng!')
    return redirect('cart_detail')

@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Đã xóa món khỏi giỏ hàng!')
    return redirect('cart_detail')

@login_required
def cart_update_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    messages.success(request, 'Đã cập nhật giỏ hàng!')
    return redirect('cart_detail')
