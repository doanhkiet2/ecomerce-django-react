from django.db import models
from orders.models import Address, Payment, Coupon
from django.conf import settings
from django.shortcuts import reverse
from django.db.models.signals import post_save


# Create your models here.

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
)


class Designer(models.Model):
    name = models.CharField(max_length=200)  # size, color
    fashion_style = models.CharField(max_length=200)
    image = models.ImageField()
    description = models.TextField()
    brand = models.ForeignKey(
        'self', related_name='brandset', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    designer = models.ForeignKey(
        Designer, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=150)
    slug = models.SlugField()
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug': self.slug})

    def get_label_meaning(self):
        key = self.label
        print("keyyyyyyy", key)
        meaning = ''
        if key == 'P':
            meaning = 'New'
        if key == 'S':
            meaning = 'Trending'
        if key == 'D':
            meaning = 'Hot Sale'
        print("meaning", meaning)

        return meaning

    def get_add_to_cart_url(self):
        return reverse('core:add-item-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('core:remove-item-from-cart', kwargs={'slug': self.slug})


class Variation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # size, color

    class Meta:
        unique_together = (
            ('item', 'name')
        )

    def __str__(self):
        return self.name


class ItemVariation(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)  # S, M , L
    attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('variation', 'value')
        )

    def __str__(self):
        return self.value


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    item_variations = models.ManyToManyField('ItemVariation')
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    time_add = models.DateTimeField(auto_now_add=True)
    pre_delete = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} {self.item.title} {self.id}"

    def get_item_with_quantity_price(self):
        return self.quantity * self.item.price

    def get_item_with_quantity_discount_price(self):
        # if self.item.discount_price:
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        # if self.item.discount_price:
        return self.get_item_with_quantity_price() - self.get_item_with_quantity_discount_price()

    def get_item_with_quantity_final_price(self):
        if self.item.discount_price:
            return self.get_item_with_quantity_discount_price()
        return self.get_item_with_quantity_price()


class Order (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    time_add = models.DateTimeField()
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address',
                                         on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address',
                                        on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(Payment,
                                on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(Coupon,
                               on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} {self.id}"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            if order_item.pre_delete:
                continue
            total += order_item.get_item_with_quantity_final_price()
        if self.coupon:
            total -= self.coupon.value
        return total

    def no_pre_delete_items(self):
        return self.items.filter(pre_delete=False)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purcharsing = models.BooleanField(default=False)
    source1 = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
