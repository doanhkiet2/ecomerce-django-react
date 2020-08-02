from django.urls import path
from .views import (CheckoutView, PaymentView, RefundView,
                    AddCouponView, )
app_name = 'orders'
urlpatterns = [
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('payment/stripe', PaymentView.as_view(), name='payment'),
    path('refund', RefundView.as_view(), name='refund'),
    path('add-coupon', AddCouponView.as_view(), name='add-coupon'),
]
