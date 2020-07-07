
from django import template
from core.models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.items.objects.filter(user=user, ordered=False)
        if qs.exists():
            count = 0
            for q in qs:
                count += q.quantity
            return count
    return 0
