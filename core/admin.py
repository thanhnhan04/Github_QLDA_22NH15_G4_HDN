from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, Order, OrderItem, Cart, CartItem
from django.db.models import Count, Sum, Q
from django.utils.html import format_html

class AdminDashboard(admin.AdminSite):
    site_header = 'Quản lý nhà hàng'
    index_template = 'admin/custom_index.html'

    def get_order_stats(self):
        return {
            'total_revenue': Order.objects.filter(status='delivered').aggregate(
                total=Sum('total'))['total'] or 0,
            'orders_by_status': Order.objects.values('status').annotate(
                count=Count('id')),
            'total_products': Product.objects.filter(is_available=True).count(),
            'top_products': OrderItem.objects.filter(
                order__status='delivered'
            ).values(
                'product_name'
            ).annotate(
                sold=Sum('quantity')
            ).order_by('-sold')[:5]
        }

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_order_stats())
        return super().index(request, extra_context)

admin_site = AdminDashboard(name='admin')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    fieldsets = (
        *UserAdmin.fieldsets,
        ('Additional Info', {'fields': ('phone', 'address', 'role')}),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # If this is an add form
            form.base_fields['role'].initial = 'admin'
        return form

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'created_at', 'get_sales_count')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    
    def get_sales_count(self, obj):
        count = OrderItem.objects.filter(
            product=obj,
            order__status='delivered'
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        return count
    get_sales_count.short_description = 'Đã bán'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_image_url', 'unit_price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total', 'status_colored', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('customer__username', 'customer__email')
    inlines = [OrderItemInline]
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'delivered': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Trạng thái'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    inlines = [CartItemInline]
