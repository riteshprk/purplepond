
from django import template
from core.models import OrderItem
register = template.Library()


@register.filter
def cart_item_count(request):
    if request.user.is_authenticated:
        qs = OrderItem.objects.filter(user=request.user, ordered=False)
        if qs.exists():
            count = 0
            for q in qs:
                count += q.quantity
            return count
    return 0
