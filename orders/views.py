from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from .models import Address, Payment, Coupon
from core.models import Order, OrderItem, UserProfile, Item
from .forms import CheckoutForm, PaymentForm, CouponForm
# Create your views here.
from orders.forms import RefundForm

import string
import random
import stripe
stripe.api_key = 'sk_test_51H0TKPKyUb1TiCEJoF5aBq4djpMWX4CQzdgE7NND4vIP2NCUYjC7yWnIln5xro6CzUMQnWeLCt2IzNZV7CmdJ2EP00IUKhvBUm'
# stripe.Charge.list(limit=3)


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_not_blank_field(fields):
    valid = True
    for fie in fields:
        if fie == '':
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'order': order,
                'form': form,
                'DISPLAY_COUPON_FORM': True,
            }
            return render(self.request, 'orders/checkout.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                shipping_address = form.cleaned_data.get('shipping_address')
                shipping_address2 = form.cleaned_data.get('shipping_address2')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                save_as_default_shipping_address = form.cleaned_data.get(
                    'save_as_default_shipping_address')
                use_default_shipping_address = form.cleaned_data.get(
                    'use_default_shipping_address')

                payment_option = form.cleaned_data.get('payment_option')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                billing_address = form.cleaned_data.get('billing_address')
                billing_address2 = form.cleaned_data.get('billing_address2')
                billing_country = form.cleaned_data.get('billing_country')
                billing_zip = form.cleaned_data.get('billing_zip')
                save_as_default_billing_address = form.cleaned_data.get(
                    'save_as_default_billing_address')
                use_default_billing_address = form.cleaned_data.get(
                    'use_default_billing_address')

                # use_default_shipping_address

                if use_default_shipping_address:
                    print('use_default_shipping_address')
                    address_qs = Address.objects.filter(
                        default=True, user=self.request.user)
                    if address_qs.exists():
                        shipping_address_obj = address_qs[0]
                        order.shipping_address = shipping_address_obj
                        order.save()
                    else:
                        messages.warning(
                            self.request, 'No shipping default available. Please entering your address.')
                        return redirect('orders:checkout')
                elif is_not_blank_field([shipping_address, shipping_country, shipping_zip]):
                    shipping_address_obj = Address.objects.create(
                        user=self.request.user,
                        street_address=shipping_address,
                        apartment_address=shipping_address2,
                        country=shipping_country,
                        default=save_as_default_shipping_address,
                        zip=shipping_zip,
                        address_type="S",
                    )
                    shipping_address_obj.save()
                    order.shipping_address = shipping_address_obj
                    order.save()
                else:
                    messages.info(
                        self.request, "Please fill in the required shipping address fields")

                # use_default_shipping_address

                if same_billing_address and shipping_address_obj:
                    # TODO
                    billing_address_obj = shipping_address_obj
                    billing_address_obj.pk = None
                    billing_address_obj.address_type = "B",
                    if save_as_default_billing_address:
                        billing_address_obj.default = True
                    billing_address_obj.default = False
                    billing_address_obj.save()
                    order.billing_address = billing_address_obj
                    order.save()

                elif use_default_billing_address:
                    # print('use_default_billing_address')
                    address_qs = Address.objects.filter(
                        default=True, user=self.request.user)
                    if address_qs.exists():
                        billing_address_obj = address_qs[0]
                        order.billing_address = billing_address_obj
                        order.save()
                    else:
                        messages.warning(
                            self.request, 'No billing default available. Please entering your address.')
                        return redirect('orders:checkout')
                elif is_not_blank_field([shipping_address, shipping_country, shipping_zip]):
                    billing_address_obj = Address.objects.create(
                        user=self.request.user,
                        street_address=billing_address,
                        apartment_address=billing_address2,
                        country=billing_country,
                        default=save_as_default_billing_address,
                        zip=billing_zip,
                        address_type="B",
                    )
                    billing_address_obj.save()
                    order.billing_address = billing_address_obj
                    order.save()
                else:
                    messages.info(
                        self.request, "Please fill in the required billing address fields")

                # print(payment_option)
                if payment_option == 'S':
                    # return redirect('core:payment', payment_option='stripe')
                    messages.success(
                        self.request, 'checkout successful, payment to finish it.')
                    return redirect('orders:payment')

                elif payment_option == 'P':
                    # return redirect('core:payment', payment_option='paypal')
                    messages.warning(
                        self.request, 'payment with paypal will open soon, please pay with stripe.')
                    return redirect('orders:payment')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('orders:checkout')
            else:
                messages.warning(
                    self.request, "form is not valid, something wrong")
                return redirect('orders:checkout')
        except ObjectDoesNotExist:
            return redirect('/')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if not order.billing_address:
                raise ObjectDoesNotExist
            form = PaymentForm()
            context = {
                'form': form,
                'order': order,
                'DISPLAY_COUPON_FORM': True,
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purcharsing:
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    context.update({
                        'default_card': card_list[0],
                    })
            print("last")

            return render(self.request, 'orders/payment.html', context)
        except:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("orders:checkout")

    def post(self, *args, **kwargs):
        db_save_above = {}
        print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("orders:checkout")
        form = PaymentForm(self.request.POST or None)
        user_profile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            stripeToken = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if user_profile.stripe_customer_id != '' and user_profile.stripe_customer_id is not None:
                    stripe_customer_id = user_profile.stripe_customer_id

                    customer = stripe.Customer.retrieve(stripe_customer_id)
                    customer.sources.create(source=stripeToken)
                    # user_profile.source1 = source['id']
                    db_save_above['user_profile'] = user_profile
                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email)
                    customer.sources.create(source=stripeToken)
                    # user_profile.source1 = source['id']
                    user_profile.stripe_customer_id = customer['id']
                    user_profile.one_click_purcharsing = True
                    db_save_above['user_profile'] = user_profile

            amount = int(order.get_total()*100)
            try:
                if save or use_default:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,
                        currency="usd",
                        customer=user_profile.stripe_customer_id,
                        # source=user_profile.source1,

                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,
                        currency="usd",
                        source=stripeToken,
                    )

                # create payment
                payment = Payment()
                payment.user = self.request.user
                payment.stripe_charge_id = charge['id']
                payment.amount = order.get_total()
                db_save_above['payment'] = payment

                order_items = order.items.filter(pre_delete=False)
                order_items.update(ordered=True)
                for order_item in order_items:
                    temp = create_ref_code()
                    db_save_above[create_ref_code()] = order_item
                    order_item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                db_save_above['order'] = order
                messages.success(self.request, "Your order was successful!")

                for key, value in db_save_above.items():
                    value.save()
                return redirect("/")
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                print(e)
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("orders:payment")


class RefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form,
        }
        return render(self.request, 'refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            try:
                order = Order.objects.get(ref_code=ref_code, ordered=True)
            except ObjectDoesNotExist:
                messages.warning(self.request, "ref_code does not exists")
                return redirect("orders:refund")
            form.save()
        messages.success(self.request, "request have been received")
        return redirect("/")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        print('step')
        if coupon.expried:
            messages.info(request, "This coupon is expried")
            return redirect("orders:checkout")
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("orders:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                coupon = get_coupon(self.request, code)
                coupon.count += 1
                order.coupon = coupon

                coupon.save()
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("orders:checkout")
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "You do not have an active order")
                return redirect("orders:checkout")

        else:
            messages.warning(self.request, "something wrong!")
            return redirect("orders:checkout")
