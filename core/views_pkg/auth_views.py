from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import User
from django import forms

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-xl rounded-pill px-4 py-3 register-input',
            'placeholder': 'Mật khẩu (ít nhất 8 ký tự, gồm chữ hoa, chữ thường và số)',
            'data-bs-toggle': 'tooltip',
            'title': 'Mật khẩu phải chứa ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số'
        }),
        help_text='Mật khẩu phải chứa ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số'
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-xl rounded-pill px-4 py-3 register-input',
            'placeholder': 'Nhập lại mật khẩu để xác nhận',
            'data-bs-toggle': 'tooltip',
            'title': 'Nhập lại chính xác mật khẩu bạn đã nhập ở trên'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address']
        labels = {
            'username': 'Tên đăng nhập',
            'email': 'Email',
            'phone': 'Số điện thoại', 
            'address': 'Địa chỉ'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-xl rounded-pill px-4 py-3 register-input',
                'placeholder': 'Tên đăng nhập từ 4-20 ký tự (chữ, số, _)',
                'pattern': '^[a-zA-Z0-9_]{4,20}$',
                'title': 'Tên đăng nhập phải từ 4-20 ký tự, chỉ bao gồm chữ cái, số và dấu gạch dưới',
                'data-bs-toggle': 'tooltip'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-xl rounded-pill px-4 py-3 register-input',
                'placeholder': 'Email của bạn (ví dụ: name@example.com)',
                'data-bs-toggle': 'tooltip',
                'title': 'Nhập địa chỉ email hợp lệ để liên hệ'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-xl rounded-pill px-4 py-3 register-input',
                'placeholder': 'Số điện thoại (VD: 0912345678)',
                'pattern': '^(0|\\+84)[0-9]{9}$',
                'title': 'Số điện thoại phải bắt đầu bằng 0 hoặc +84 và có 10 chữ số',
                'data-bs-toggle': 'tooltip'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-xl rounded-pill px-4 py-3 register-input',
                'placeholder': 'Địa chỉ giao hàng của bạn',
                'data-bs-toggle': 'tooltip',
                'title': 'Nhập địa chỉ đầy đủ để giao hàng'
            })
        }
        help_texts = {
            'username': 'Chỉ sử dụng chữ cái, số và dấu gạch dưới (_), độ dài 4-20 ký tự',
            'email': 'Nhập địa chỉ email hợp lệ để liên hệ',
            'phone': 'Số điện thoại bắt đầu bằng 0 hoặc +84, có 10 chữ số',
            'address': 'Nhập địa chỉ đầy đủ để giao hàng'
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Mật khẩu không khớp")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4 or len(username) > 20:
            raise forms.ValidationError("Tên đăng nhập phải từ 4-20 ký tự")
        if not username.isalnum() and '_' not in username:
            raise forms.ValidationError("Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã được sử dụng")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        if not re.match(r'^(0|\+84)[0-9]{9}$', phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ. Phải bắt đầu bằng 0 hoặc +84 và có 10 chữ số")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Số điện thoại đã được sử dụng")
        return phone

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ hoa")
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ thường")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ số")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'customer'  # Đảm bảo user đăng ký mới luôn có role là customer
        if commit:
            user.save()
        return user

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/auth/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'admin':  # Kiểm tra role admin
                return redirect('admin_home')  # Chuyển hướng đến trang chủ admin
            else:
                return redirect('home')  # Chuyển hướng đến trang chủ người dùng
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    return render(request, 'core/auth/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.save()
        messages.success(request, 'Cập nhật thông tin thành công!')
        return redirect('profile')
    
    # Use admin template for admin users
    if request.user.role == 'admin':
        template = 'core/admin/profile.html'
    else:
        template = 'core/auth/profile.html'
    
    return render(request, template)
