import os
import json
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, ProductForm
from .models import (Item,
                     OrderItem,
                     Order,
                     Address,
                     Payment,
                     Coupon,
                     Refund,
                     UserProfile)
import random
import string
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # settings.STRIPE_SECRET_KEY
print(stripe.api_key)


def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CategoryView(ListView):
    paginate_by = 8
    template_name = "home-page.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            qs = Item.objects.filter(title__icontains=query)
            return qs
        else:
            qs = Item.objects.filter(category=self.kwargs['category'])
            print(qs)
            return qs


class HomeView(ListView):
    paginate_by = 8
    template_name = "home-page.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            qs = Item.objects.filter(title__icontains=query)
            print(qs)
            return qs
        else:
            qs = Item.objects.order_by('?')
            return qs


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.filter(
                user=self.request.user, ordered=False).order_by('pk').first()
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        form = ProductForm()
        context['form'] = form
        return context
    # def post():
    #     form = ProductForm(request.POST or None)
    #     if form.is_valid():
    #         try:
    #             get_size = form.cleaned_data.get('item_size')
    #             print(get_size)
    #             messages.success(self.request, get_size)
    #             return redirect("core:checkout")
    #         except ObjectDoesNotExist:
    #             messages.info(self.request, "You do not have an active order")
    #             return redirect("core:checkout")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            # code = form.cleaned_data.get('code')
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update({
                    'default_shipping_address': shipping_address_qs[0]
                })

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update({
                    'default_billing_address': billing_address_qs[0]
                })

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print('using the default shipping address')
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')

                else:
                    print("User is entering new shipping address")

                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    print(shipping_address1, 'hello')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    print(shipping_country)

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                        return redirect('core:checkout')
                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    print('using the default billing address')
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')

                else:
                    print("User is entering new billing address")

                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")
                        return redirect('core:checkout')
                # TODO: redirect to selected payment option
                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        pay_option = self.kwargs['payment_option']
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.userprofile
            if pay_option == 'stripe':
                if userprofile.one_click_purchasing:
                    # fetch the users card list
                    cards = stripe.Customer.list_sources(
                        userprofile.stripe_customer_id,
                        limit=3,
                        object='card'
                    )
                    card_list = cards['data']
                    if len(card_list) > 0:
                        # update the context with the default card
                        context.update({
                            'card': card_list[0]
                        })
                return render(self.request, "payment.html", context)
            else:
                if pay_option == 'paypal':
                    return render(self.request, "paypalpayment.html", context)
                else:
                    messages.warning(
                        self.request, "Please select correct payment option")
                    return redirect("core:checkout")
        else:
            messages.warning(
                self.request, "You have not added billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)
                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                userprofile.one_click_purchasing = True
                userprofile.save()
            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.ordereditem_title = item.item.title
                    item.ordereditem_price = item.item.price
                    item.ordereditem_totalprice = item.get_final_price()
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                if order.coupon:
                    order.order_discount_amount = order.coupon.amount
                order.order_total = order.get_total()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect('/payment/stripe/'+order.ref_code)
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('messages')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, 'Too many requests')
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, 'Invalid parameters')
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, 'Authentication failed')
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, 'Network error')
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again")
                return redirect("/")

            except Exception as e:
                # Something else happened, completely unrelated to Stripe.
                # It is related to us. Send notification as mail
                #"A serious error has been occure. We have been notified"
                messages.warning(self.request, e)
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


@login_required
def paypal_transaction(request):
    order = Order.objects.get(user=request.user, ordered=False)

    if request.method == 'POST':
        # request.raw_post_data w/ Django < 1.4
        json_data = json.loads(request.body)
        try:
            data = json_data['orderID']
        # create the payment
            payment = Payment()
            payment.stripe_charge_id = data
            payment.user = request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.ordereditem_title = item.item.title
                item.ordereditem_price = item.item.price
                item.ordereditem_totalprice = item.get_final_price()
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            if order.coupon:
                order.order_discount_amount = order.coupon.amount
            order.order_total = order.get_total()
            order.save()
            messages.success(request, "Your order was successful!")
            return JsonResponse({'success': True, 'order_ref_code': order.ref_code})

        except Exception as e:
            print(e)
            messages.success(
                request, "Your order was not successful! Try again")
            return JsonResponse({'success': False})


@login_required
def add_to_cart(request, slug):
    form = ProductForm(request.POST or None)
    get_size = ''
    if form.is_valid():
        get_size = form.cleaned_data.get('item_size')
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered_size=get_size,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug, ordered_size=get_size).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("core:product", slug=slug)
            else:
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
                return redirect("core:product", slug=slug)
        else:
            order_date = timezone.now()
            order = Order.objects.create(
                user=request.user, order_date=order_date)
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:product", slug=slug)
    messages.info(request, "Please add product in your cart.")
    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug, size):
    order_item = OrderItem.objects.filter(
        user=request.user,
        item__slug=slug,
        ordered_size=size,
        ordered=False
    )[0]
    if order_item:
        order_item.delete()
        order = order_item.Order_set.all()
        order.delete()
        messages.info(request, "This item was removed from your cart.")
        return redirect("core:order-summary")
    else:

        messages.info(request, "This item was not in your cart")
        return redirect("core:product", slug=slug)


@login_required
def add_single_item_to_cart(request, slug, size):
    #item = get_object_or_404(Item, slug=slug)
    order = OrderItem.objects.filter(
        user=request.user,
        item__slug=slug,
        ordered_size=size,
        ordered=False
    )[0]
    if order:
        #order = order_qs[0]
        # check if the order item is in the order

        order.quantity += 1
        order.save()
        messages.info(request, "This item quantity was updated.")
        return redirect("core:order-summary")
    else:
        messages.info(request, "This item was not in your cart")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug, size):
    #item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.filter(
        user=request.user,
        item__slug=slug,
        ordered_size=size,
        ordered=False
    )[0]
    if order_item:
       # order = order_qs[0]
        # check if the order item is in the order

        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order_item.delete()
            order = order_item.Order_set.all()
            order.delete()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
    else:
        messages.info(request, "This item was not in your cart")
        return redirect("core:product", slug=slug)


@login_required
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        return None


class AddCouponView(View):
    def post(self, *args, **kwargs):

        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                if get_coupon(self.request, code):
                    order.coupon = get_coupon(self.request, code)
                    order.save()
                    messages.success(self.request, "Successfully added coupon")
                    return redirect("core:checkout")
                messages.info(self.request, "Coupon is not valid or expired")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")
        else:
            messages.info(self.request, "Please enter valid promo-code")
            return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


class MyAccount(View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.filter(
                user=self.request.user, ordered=True).order_by('-order_date')
            user_detail = self.request.user
            context = {
                'object': order,
                'user': user_detail
            }
            return render(self.request, 'account_detail.html', context)
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "You do not have an completed order")
            return render(self.request, 'account_detail.html', context)

    def post(self, *args, **kwargs):
        #form = RefundForm(self.request.POST)
        pass


def order_confirmation(request, payment_option, order_ref_code):
    order = Order.objects.get(ref_code=order_ref_code) or None
    context = {
        'order': order
    }
    return render(request, 'order_confirmation.html', context)
