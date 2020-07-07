
from django import template
from django.http import HttpResponse, request
from core.models import OrderItem

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = OrderItem.objects.filter(user=user, ordered=False)
        if qs.exists():
            count = 0
            for q in qs:
                count += q.quantity

            return count
    return 0


request.session['cart'] = cart_item_count
