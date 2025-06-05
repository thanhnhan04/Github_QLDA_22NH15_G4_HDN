from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Order, Promotion, Notification, User
from datetime import timedelta

class Command(BaseCommand):
    help = 'Tạo thông báo nhắc nhở đơn hàng chưa hoàn tất và khuyến mãi sắp hết hạn cho khách hàng.'

    def handle(self, *args, **options):
        now = timezone.now()
        # Đơn hàng chưa hoàn tất (pending/processing > 24h)
        orders = Order.objects.filter(status__in=['pending', 'processing'], created_at__lte=now - timedelta(hours=24))
        for order in orders:
            msg = f'Bạn có đơn hàng #{order.id} chưa hoàn tất. Vui lòng kiểm tra lại đơn hàng.'
            Notification.objects.get_or_create(
                user=order.customer,
                message=msg,
                url=f'/orders/{order.id}/',
                is_read=False
            )
        # Khuyến mãi sắp hết hạn (trong 3 ngày tới)
        soon = now + timedelta(days=3)
        promotions_ending = Promotion.objects.filter(is_active=True, end_date__range=(now, soon))
        for promo in promotions_ending:
            users = order.customer.__class__.objects.filter(role='customer', is_active=True)
            for user in users:
                msg = f'Mã khuyến mãi {promo.code} sắp hết hạn vào {promo.end_date.strftime("%d/%m/%Y")}. Đừng bỏ lỡ!'
                Notification.objects.get_or_create(
                    user=user,
                    message=msg,
                    url='/orders/create/',
                    is_read=False
                )
        # Khuyến mãi sắp diễn ra (trong 3 ngày tới)
        promotions_starting = Promotion.objects.filter(is_active=True, start_date__range=(now, soon))
        for promo in promotions_starting:
            users = order.customer.__class__.objects.filter(role='customer', is_active=True)
            for user in users:
                msg = f'Mã khuyến mãi {promo.code} sẽ bắt đầu từ {promo.start_date.strftime("%d/%m/%Y")}: {promo.description}'
                Notification.objects.get_or_create(
                    user=user,
                    message=msg,
                    url='/orders/create/',
                    is_read=False
                )
        # Thông báo cho admin về đơn hàng mới (trong 5 tiếng gần nhất)
        admin_users = User.objects.filter(role='admin', is_active=True)
        new_orders = Order.objects.filter(status='pending', created_at__gte=now - timedelta(hours=5))
        for order in new_orders:
            msg = f'Đơn hàng mới #{order.id} vừa được đặt bởi {order.customer.username}.'
            for admin in admin_users:
                Notification.objects.get_or_create(
                    user=admin,
                    message=msg,
                    url=f'/admin-panel/orders/{order.id}/',
                    is_read=False
                )
        # Thông báo cho khách hàng về trạng thái các đơn hàng
        all_orders = Order.objects.filter(status__in=['pending', 'processing', 'delivered', 'cancelled'])
        for order in all_orders:
            status_text = dict(Order.STATUS_CHOICES).get(order.status, order.status)
            Notification.objects.get_or_create(
                user=order.customer,
                message=f'Trạng thái đơn hàng #{order.id} hiện tại: {status_text}',
                url=f'/orders/{order.id}/',
                is_read=False
            )
        # Thông báo nhắc nhở khách hàng bỏ giỏ hàng chưa đặt đơn
        cart_timeout = now - timedelta(minutes=1)  # Đổi thành 5 phút chưa đặt đơn sẽ nhắc
        from core.models import Cart
        carts = Cart.objects.filter(items__isnull=False, updated_at__lte=cart_timeout)
        for cart in carts:
            user = cart.user
            # Kiểm tra user chưa có đơn hàng "pending" hoặc "processing" mới trong 5 phút
            recent_order = Order.objects.filter(customer=user, created_at__gte=cart_timeout, status__in=['pending', 'processing']).exists()
            if not recent_order:
                Notification.objects.get_or_create(
                    user=user,
                    message="Bạn có sản phẩm trong giỏ hàng chưa đặt đơn. Đừng bỏ lỡ món ngon!",
                    url="/cart/",
                    is_read=False
                )
        self.stdout.write(self.style.SUCCESS('Đã tạo thông báo nhắc nhở cho khách hàng.'))
