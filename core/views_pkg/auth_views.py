from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import User
from django import forms

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Xác nhận mật khẩu', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address']
        labels = {
            'username': 'Tên đăng nhập',
            'email': 'Email',
            'phone': 'Số điện thoại',
            'address': 'Địa chỉ'
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Mật khẩu không khớp")
        return password2

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
