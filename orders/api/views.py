
# stripe.api_key = settings.STRIPE_SECRET_KEY
import string
import random
from core.models import Order, UserProfile
from orders.models import Address, Coupon, Payment
import stripe
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
# from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.http import Http404
from django.conf import settings
from core.api.serializers import PaymentSerializer
from rest_framework.permissions import IsAuthenticated
# stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = 'sk_test_51H6g4WEIs0qYXInvtJO90rrP4f4bNwBpghTAUD9rdM17vsWfKK2A1qJMbDZtofBJdIPH1Go72xGssh0IA3BMTg3E005A17O9bp'


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_not_blank_field(fields):
    valid = True
    for fie in fields:
        if fie == '':
            valid = False
    return valid


class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        # db_save_above = {}
        # try:
        #     order = Order.objects.get(user=self.request.user, ordered=False)
        # except ObjectDoesNotExist:
        #     return Response({'message': 'not found order'}, status=HTTP_400_BAD_REQUEST)
        # form = PaymentForm(self.request.POST or None)
        user_profile = UserProfile.objects.get(user=self.request.user)
        stripeToken = request.data.get('stripeToken')
        billing_address_id = request.data.get('selectedBillingAddress')
        shipping_address_id = request.data.get('selectedShippingAddress')
        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)
        # save = form.cleaned_data.get('save')
        # use_default = form.cleaned_data.get('use_default')
        # save = False
        # use_default = False
        # if save:

        if user_profile.stripe_customer_id != '' and user_profile.stripe_customer_id is not None:
            stripe_customer_id = user_profile.stripe_customer_id

            customer = stripe.Customer.retrieve(stripe_customer_id)
            customer.sources.create(source=stripeToken)
            # user_profile.source1 = source['id']
            # db_save_above['user_profile'] = user_profile
            # user_profile.save()

        else:
            customer = stripe.Customer.create(
                email=self.request.user.email)
            customer.sources.create(source=stripeToken)
            # user_profile.source1 = source['id']
            user_profile.stripe_customer_id = customer['id']
            user_profile.one_click_purcharsing = True
            # db_save_above['user_profile'] = user_profile
            user_profile.save()

        amount = int(order.get_total() * 100)
        try:
            # if save or use_default:
            #     # charge the customer because we cannot charge the token more than once
            #     charge = stripe.Charge.create(
            #         amount=amount,
            #         currency="usd",
            #         customer=user_profile.stripe_customer_id,
            #         # source=user_profile.source1,

            #     )
            # else:
            # charge once off on the token
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                # source=stripeToken,
                customer=user_profile.stripe_customer_id
            )

            # create payment
            payment = Payment()
            payment.user = self.request.user
            payment.stripe_charge_id = charge['id']
            payment.amount = order.get_total()
            # db_save_above['payment'] = payment
            payment.save()

            order_items = order.items.filter(pre_delete=False)
            order_items.update(ordered=True)
            for order_item in order_items:
                temp = create_ref_code()
                # db_save_above[create_ref_code()] = order_item
                order_item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            # db_save_above['order'] = order
            order.save()

            # for key, value in db_save_above.items():
            #     value.save()
            return Response({'message': 'Your order was successful!'}, status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return Response({'message': 'Rate limit error'}, status=HTTP_400_BAD_REQUEST)
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print("aaaaaaaaaaaaaaa", e)
            return Response({'message': 'Invalid parameters'}, status=HTTP_400_BAD_REQUEST)
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({'message': 'Not authenticated'}, status=HTTP_400_BAD_REQUEST)
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({'message': 'Network error'}, status=HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            print(e)
            return Response({'message': 'Something went wrong. You were not charged. Please try again.'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            # send an email to ourselves
            print(e)
            return Response({'message': 'A serious error occurred. We have been notifed.'}, status=HTTP_400_BAD_REQUEST)
        return Response({'message': 'Invalid data received'}, status=HTTP_400_BAD_REQUEST)


def get_coupon(request, code):
    coupon = get_object_or_404(Coupon, code=code)
    if coupon.expried:
        # TODO
        raise Http404("expried")
    return coupon


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)

        if code is None:
            return Response({'message': 'Invalid data received'}, status=HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(
                user=self.request.user, ordered=False)
            coupon = get_coupon(self.request, code)
            coupon.count += 1
            order.coupon = coupon

            coupon.save()
            order.save()
            return Response({'message': 'Successfully added coupon'}, status=HTTP_200_OK)

        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")


class PaymentListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-timestamp')
