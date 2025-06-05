from django import forms
from .models import Promotion, OrderReview

class PromotionForm(forms.ModelForm):
    start_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    class Meta:
        model = Promotion
        fields = ['code', 'description', 'discount_percent', 'discount_amount', 'min_order_total', 'start_date', 'end_date', 'is_active']

class OrderReviewForm(forms.ModelForm):
    class Meta:
        model = OrderReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} sao') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Nhận xét của bạn...'}),
        }
        labels = {
            'rating': 'Đánh giá',
            'comment': 'Nhận xét',
        }
