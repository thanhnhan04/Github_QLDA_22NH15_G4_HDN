from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return Decimal('0')

@register.filter(name='cart_total')
def cart_total(cart):
    if not cart or not cart.items.exists():
        return 0
    return sum(item.price * item.quantity for item in cart.items.all())

@register.filter(name='format_price')
def format_price(value):
    """
    Format a number as Vietnamese currency
    Example: 45000 -> 45.000 VNĐ
    """
    try:
        # Format the price value directly 
        number = int(float(value))
        return "{:,.0f} VNĐ".format(number).replace(",", ".")
    except (ValueError, TypeError):
        return "0 VNĐ"

@register.filter(name='startswith')
def startswith(text, starts):
    """Return True if text starts with the given substring."""
    if not isinstance(text, str):
        return False
    return text.startswith(starts)

@register.filter(name='contains')
def contains(text, substring):
    """Return True if substring is in text."""
    if not isinstance(text, str):
        return False
    return substring in text
