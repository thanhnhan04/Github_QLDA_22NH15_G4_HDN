from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from ..models import Order, OrderItem, Cart, User, Promotion, OrderReview
from django import forms
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.forms import OrderReviewForm

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
    now = timezone.now()
    available_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )
    discount = 0
    promo_error = ''
    promo_code = request.POST.get('promo_code', '').strip() if request.method == 'POST' else ''
    promo = None
    if promo_code:
        try:
            promo = Promotion.objects.get(code=promo_code, is_active=True, start_date__lte=now, end_date__gte=now)
            if cart_total < promo.min_order_total:
                promo_error = f'Đơn tối thiểu {promo.min_order_total} VNĐ để áp dụng mã này.'
                promo = None
        except Promotion.DoesNotExist:
            promo_error = 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn.'
    if promo:
        if promo.discount_percent:
            discount = cart_total * promo.discount_percent / 100
        elif promo.discount_amount:
            discount = promo.discount_amount
        if discount > cart_total:
            discount = cart_total
    final_total = cart_total - discount
    if request.method == 'POST' and not promo_error:
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                total=final_total,
                status='pending',
                payment_method=request.POST.get('payment_method'),
                note=request.POST.get('note', '')
            )
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product_name,
                    product_image_url=cart_item.product_image_url,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price,
                    total_price=cart_item.price * cart_item.quantity
                )
            cart.items.all().delete()
            messages.success(request, f'Đơn hàng #{order.id} đã được tạo thành công!')
            return redirect('order_detail', pk=order.id)
    return render(request, 'core/order/create.html', {
        'cart': cart,
        'total': cart_total,
        'final_total': final_total,
        'discount': discount,
        'promo_code': promo_code,
        'promo_error': promo_error,
        'available_promotions': available_promotions,
        'payment_methods': Order.PAYMENT_CHOICES,
        'now': now,
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
    review = None
    review_form = None
    can_review = False
    if request.user.role == 'customer' and order.status == 'delivered':
        try:
            review = order.review
        except OrderReview.DoesNotExist:
            review = None
        if review is None:
            can_review = True
            if request.method == 'POST' and 'review_submit' in request.POST:
                review_form = OrderReviewForm(request.POST)
                if review_form.is_valid():
                    OrderReview.objects.create(
                        order=order,
                        customer=request.user,
                        rating=review_form.cleaned_data['rating'],
                        comment=review_form.cleaned_data['comment']
                    )
                    messages.success(request, 'Cảm ơn bạn đã đánh giá đơn hàng!')
                    return redirect('order_detail', pk=order.id)
            else:
                review_form = OrderReviewForm()
    context = {'order': order, 'review': review, 'review_form': review_form, 'can_review': can_review}
    return render(request, 'core/order/detail.html', context)

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

@login_required
@require_http_methods(["GET", "POST"])
def order_confirm(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.items.exists():
        messages.error(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('cart_detail')
    now = timezone.now()
    total = sum(item.price * item.quantity for item in cart.items.all())
    payment_method = request.POST.get('payment_method', '')
    note = request.POST.get('note', '')
    promo_code = request.POST.get('promo_code', '').strip()
    discount = 0
    promo = None
    promo_error = ''
    if promo_code:
        try:
            promo = Promotion.objects.get(code=promo_code, is_active=True, start_date__lte=now, end_date__gte=now)
            if total < promo.min_order_total:
                promo_error = f'Đơn tối thiểu {promo.min_order_total} VNĐ để áp dụng mã này.'
                promo = None
        except Promotion.DoesNotExist:
            promo_error = 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn.'
    if promo:
        if promo.discount_percent:
            discount = total * promo.discount_percent / 100
        elif promo.discount_amount:
            discount = promo.discount_amount
        if discount > total:
            discount = total
    final_total = total - discount
    if request.method == 'POST' and request.POST.get('confirm') == '1':
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                total=final_total,
                status='pending',
                payment_method=payment_method,
                note=note
            )
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product_name,
                    product_image_url=cart_item.product_image_url,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price,
                    total_price=cart_item.price * cart_item.quantity
                )
            cart.items.all().delete()
            messages.success(request, f'Đơn hàng #{order.id} đã được tạo thành công!')
            return redirect('order_detail', pk=order.id)
    return render(request, 'core/order/confirm.html', {
        'cart': cart,
        'user': request.user,
        'total': total,
        'discount': discount,
        'final_total': final_total,
        'payment_method': payment_method,
        'note': note,
        'promo_code': promo_code,
        'promo_error': promo_error,
    })

@login_required
def ajax_promotion_calculate(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)
        cart_total = sum(item.price * item.quantity for item in cart.items.all())
        promo_code = request.POST.get('promo_code', '').strip()
        discount = 0
        promo_error = ''
        now = timezone.now()
        promo = None
        if promo_code:
            try:
                promo = Promotion.objects.get(code=promo_code, is_active=True, start_date__lte=now, end_date__gte=now)
                if cart_total < promo.min_order_total:
                    promo_error = f'Đơn tối thiểu {promo.min_order_total} VNĐ để áp dụng mã này.'
                    promo = None
            except Promotion.DoesNotExist:
                promo_error = 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn.'
        if promo:
            if promo.discount_percent:
                discount = cart_total * promo.discount_percent / 100
            elif promo.discount_amount:
                discount = promo.discount_amount
            if discount > cart_total:
                discount = cart_total
        final_total = cart_total - discount
        return JsonResponse({
            'cart_total': int(cart_total),
            'discount': int(discount),
            'final_total': int(final_total),
            'promo_error': promo_error
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
