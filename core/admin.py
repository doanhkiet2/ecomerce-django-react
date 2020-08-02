from django.contrib import admin
from .models import Order, OrderItem, Item, UserProfile, Variation, ItemVariation
from orders.models import Address, Payment, Refund, Coupon
from core.models import Designer


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin (admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'

    ]

    list_filter = [
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
    ]

    search_fields = [
        'user__username',
        'ref_code'
    ]

    actions = [make_refund_accepted]


class AddressAdmin (admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default',
    ]
    list_display_links = [
        'user',
    ]

    list_filter = [
        'country',
        'address_type',
        'default',
    ]

    search_fields = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
    ]

    actions = [make_refund_accepted]


class ItemVariationInlineAdmin(admin.TabularInline):
    model = ItemVariation
    extra = 1


class ItemVariationAdmin (admin.ModelAdmin):
    list_display = [
        'variation',
        'value',
        'attachment',
    ]

    list_filter = [
        'variation', 'variation__item'
    ]

    search_fields = [
        'value',
    ]


class VariationAdmin (admin.ModelAdmin):
    list_display = [
        'item',
        'name',
    ]

    list_filter = [
        'item'
    ]

    search_fields = [
        'name',
    ]
    inlines = [ItemVariationInlineAdmin]


admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(Payment)
admin.site.register(Refund)
admin.site.register(Coupon)
admin.site.register(Designer)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ItemVariation, ItemVariationAdmin)
