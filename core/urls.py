from django.urls import path
from .views import (
    HomeView,
    OrderSummaryView,
    CheckoutView,
    ItemDetailView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('order_summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add_to_cart/<slug>/<size>', add_to_cart, name='add_to_cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove_from_cart/<slug>', remove_from_cart, name='remove_from_cart'),
    path('remove-item-from-cart/<slug>/<size>', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund')
]
