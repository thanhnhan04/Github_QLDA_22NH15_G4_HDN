from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ..models import Product, Category
from django import forms

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image_url', 'is_available']
        labels = {
            'name': 'Tên món',
            'description': 'Mô tả',
            'price': 'Giá (VNĐ)',
            'category': 'Danh mục',
            'image_url': 'Đường dẫn ảnh',
            'is_available': 'Có sẵn'
        }

def product_list(request):
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    return render(request, 'core/product/list.html', {
        'products': products,
        'categories': categories
    })

@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm món mới thành công!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'core/product/form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật món thành công!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product/form.html', {'form': form, 'action': 'Edit'})

@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Đã xóa món thành công!')
    return redirect('product_list')
