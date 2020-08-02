from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Refund

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal'),
)


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'required': True,
            'class': 'custom-select d-block w-100 toggle-required'
        }))
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'required': True,
            'class': 'custom-select d-block w-100 toggle-required'
        }))
    shipping_zip = forms.CharField(required=False)
    billing_zip = forms.CharField(required=False)
    same_billing_address = forms.BooleanField(required=False)
    save_as_default_shipping_address = forms.BooleanField(required=False)
    save_as_default_billing_address = forms.BooleanField(required=False)
    use_default_shipping_address = forms.BooleanField(required=False)
    use_default_billing_address = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class RefundForm(forms.ModelForm):
    # ref_code = forms.CharField(max_length=20, min_length=20)
    class Meta:
        model = Refund
        fields = ['ref_code', 'email', 'phone', 'message']


class CouponForm(forms.Form):
    code = forms.CharField()
