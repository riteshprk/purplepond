
from django import template
from core.models import Order, OrderItem

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = OrderItem.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].item.count()
    return 0
