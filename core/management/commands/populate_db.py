from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Category, Product
from django.db import transaction

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        with transaction.atomic():
            # Create admin user
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',
                    role='admin',
                    phone='1234567890',
                    address='123 Admin Street'
                )
                self.stdout.write(self.style.SUCCESS('Created admin user'))

            # Create categories
            categories_data = [
                'Món Việt Nam',
                'Cơm & Bún',
                'Đồ nướng',
                'Món lẩu',
                'Món gà',
                'Đồ ăn kèm',
                'Đồ uống',
                'Tráng miệng'
            ]

            for cat_name in categories_data:
                category, created = Category.objects.get_or_create(name=cat_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created category: {cat_name}'))

            products_data = [
                # Món Việt Nam
                {
                    'category': 'Món Việt Nam',
                    'name': 'Phở Bò',
                    'description': 'Phở bò truyền thống với nước dùng đậm đà, thịt bò tươi và các loại rau thơm',
                    'price': 45000, # 45.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1503764654157-72d979d9af2f?w=500'
                },
                {
                    'category': 'Món Việt Nam',
                    'name': 'Bánh Mì Thịt',
                    'description': 'Bánh mì giòn với thịt nướng, patê, rau sống và đồ chua',
                    'price': 25000, # 25.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1509722747041-616f39b57569?w=500'
                },
                # Cơm & Bún
                {
                    'category': 'Cơm & Bún',
                    'name': 'Cơm Tấm Sườn',
                    'description': 'Cơm tấm với sườn nướng, trứng ốp la, bì và đồ chua',
                    'price': 40000, # 40.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500'
                },
                {
                    'category': 'Cơm & Bún',
                    'name': 'Bún Thịt Nướng',
                    'description': 'Bún với thịt nướng, chả giò, rau sống và nước mắm',
                    'price': 35000, # 35.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1552611052-33e04de081de?w=500'
                },
                # Đồ nướng
                {
                    'category': 'Đồ nướng',
                    'name': 'Ba Chỉ Nướng',
                    'description': 'Ba chỉ nướng thơm ngon với sốt đặc biệt',
                    'price': 75000, # 75.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=500'
                },
                {
                    'category': 'Đồ nướng',
                    'name': 'Sườn Nướng',
                    'description': 'Sườn nướng với sốt BBQ đặc biệt',
                    'price': 85000, # 85.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?w=500'
                },
                # Món lẩu
                {
                    'category': 'Món lẩu',
                    'name': 'Lẩu Thái',
                    'description': 'Lẩu Thái chua cay với hải sản và nấm',
                    'price': 159000, # 159.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1583032015879-e5022cb87c3b?w=500'
                },
                {
                    'category': 'Món lẩu',
                    'name': 'Lẩu Hải Sản',
                    'description': 'Lẩu hải sản với nước dùng đặc biệt',
                    'price': 199000, # 199.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1526069631228-723c945bea6b?w=500'
                },
                # Món gà
                {
                    'category': 'Món gà',
                    'name': 'Gà Nướng',
                    'description': 'Gà nướng nguyên con với xốt đặc biệt',
                    'price': 165000, # 165.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1562967914-01efa7e87832?w=500'
                },
                {
                    'category': 'Món gà',
                    'name': 'Gà Chiên',
                    'description': 'Gà chiên giòn với sốt cay',
                    'price': 145000, # 145.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1587593810167-a84920ea0d17?w=500'
                },
                # Đồ ăn kèm
                {
                    'category': 'Đồ ăn kèm',
                    'name': 'Khoai Tây Chiên',
                    'description': 'Khoai tây chiên giòn với sốt mayonnaise',
                    'price': 29000, # 29.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1585109649139-366815a0d713?w=500'
                },
                {
                    'category': 'Đồ ăn kèm',
                    'name': 'Salad Trộn',
                    'description': 'Salad tươi với sốt dầu giấm',
                    'price': 35000, # 35.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=500'
                },
                # Đồ uống
                {
                    'category': 'Đồ uống',
                    'name': 'Nước Ngọt',
                    'description': 'Các loại nước ngọt có ga',
                    'price': 15000, # 15.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=500'
                },
                {
                    'category': 'Đồ uống',
                    'name': 'Trà Đào',
                    'description': 'Trà đào tươi mát với đào miếng',
                    'price': 25000, # 25.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=500'
                },
                # Tráng miệng
                {
                    'category': 'Tráng miệng',
                    'name': 'Chè Thái',
                    'description': 'Chè Thái thơm ngon với các loại trái cây',
                    'price': 35000, # 35.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=500'
                },
                {
                    'category': 'Tráng miệng',
                    'name': 'Bánh Flan',
                    'description': 'Bánh flan mềm mịn với caramel',
                    'price': 20000, # 20.000 VNĐ
                    'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=500'
                },
            ]

            for product_data in products_data:
                category = Category.objects.get(name=product_data['category'])
                product, created = Product.objects.get_or_create(
                    name=product_data['name'],
                    defaults={
                        'category': category,
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'image_url': product_data['image_url'],
                        'is_available': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
