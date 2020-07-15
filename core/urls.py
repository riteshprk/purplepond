from django.urls import path
from .views import (
    HomeView,
    OrderSummaryView,
    CheckoutView,
    ItemDetailView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    add_single_item_to_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    CategoryView,
    paypal_transaction,
    MyAccount,
    order_confirmation
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('category/<category>', CategoryView.as_view(), name='categories'),
    path('product/<slug>', ItemDetailView.as_view(), name='product'),
    path('order_summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add_to_cart/<slug>', add_to_cart, name='add_to_cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove_from_cart/<slug>/<size>',
         remove_from_cart, name='remove_from_cart'),
    path('remove-item-from-cart/<slug>/<size>', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('add-item-to-cart/<slug>/<size>', add_single_item_to_cart,
         name='add-single-item-to-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('payment/paypal/capture-paypal-transaction',
         paypal_transaction, name='paypalpayment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('myaccount/', MyAccount.as_view(), name='myaccount'),
    path('order/<order_ref_code>',
         order_confirmation, name='order_confirmation')


]
