from django.db import models, transaction
from django.conf import settings
from django_countries.fields import CountryField
from datetime import date
# Create your models here.
ADDRESS_CHOICES = (
    ('S', 'Shipping'),
    ('B', 'Billing'),
)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    apartment_address = models.CharField(max_length=200)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(choices=ADDRESS_CHOICES, max_length=1)
    time_add = models.DateTimeField(auto_now_add=True)
    default = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} {self.id}'

    def save(self, *args, **kwargs):
        if not self.default:
            return super(Address, self).save(*args, **kwargs)
        with transaction.atomic():
            Address.objects.filter(
                default=True, address_type=self.address_type, user=self.user).update(default=False)
            return super(Address, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=50)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Refund (models.Model):
    ref_code = models.CharField(max_length=20)
    message = models.TextField()
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    time_add = models.DateField(auto_now_add=True)


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    value = models.IntegerField()
    count = models.IntegerField(default=0)
    # TODO: check
    days_active = models.IntegerField(default=365)
    time_add = models.DateTimeField(auto_now_add=True)
    time_expried = models.DateField(null=True, blank=True)

    @property
    def expried(self):
        return date.today() > self.time_expried
