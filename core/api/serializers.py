from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from core.models import Designer, Item, ItemVariation, Order, OrderItem, Variation
from orders.models import Coupon, Address, Payment


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            'id',
            'code',
            'value',
            'days_active',
            'time_expried',
        )


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id',
            'title',
            'slug',
            'price',
            'discount_price',
            'add_time',
            'image',
            'category',
            'label',
            'description',
        )

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    count_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_items',
            'count_items',
            'total',
            'coupon',
        )

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_count_items(self, obj):
        return obj.no_pre_delete_items().count()

    def get_total(self, obj):
        return obj.get_total()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None


class ItemVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVariation
        fields = (
            'id',
            'value',
            'attachment',
        )


class VariationSerializer(serializers.ModelSerializer):
    item_variations = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = (
            'id',
            'name',
            'item_variations',
        )

    def get_item_variations(self, obj):
        return ItemVariationSerializer(obj.itemvariation_set.all(), many=True).data


class DesignerDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    brand_designers = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    class Meta:
        model = Designer
        fields = (
            "id",
            "name",
            "image",  # TOKNOW: full url
            "fashion_style",
            "description",
            "brand",
            "items",
            'brand_designers',
        )

    def get_items(self, obj):
        return ItemDetailSerializer(obj.item_set.all(), many=True).data

    def get_brand_designers(self, obj):
        return DesignerDetailSerializer(obj.brandset.all(), many=True).data

    def get_brand(self, obj):
        # TOKNOW
        if obj.brand:
            return {"id": obj.brand.id, "name": obj.brand.name}
        return None


class ItemDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    variations = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id',
            'title',
            'slug',
            'price',
            'discount_price',
            'add_time',
            'image',  # TOKNOW: sort url
            'category',
            'label',
            'description',
            'variations',
        )

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()

    def get_variations(self, obj):
        return VariationSerializer(obj.variation_set.all(), many=True).data


class VariationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = (
            'id',
            'name',
        )


class ItemVariationDetailSerializer(serializers.ModelSerializer):
    variation = serializers.SerializerMethodField()

    class Meta:
        model = ItemVariation
        fields = (
            'id',
            'variation',
            'value',
            'attachment',
        )

    def get_variation(self, obj):
        return VariationDetailSerializer(obj.variation).data


class OrderItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()
    item_variations = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'item',
            'quantity',
            'pre_delete',
            'final_price',
            'item_variations',
        )

    def get_item(self, obj):
        return ItemSerializer(obj.item).data

    def get_item_variations(self, obj):
        return ItemVariationDetailSerializer(obj.item_variations.all(), many=True).data

    def get_final_price(self, obj):
        return obj.get_item_with_quantity_final_price()


class AddressSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)

    class Meta:
        model = Address

        fields = (
            'id',
            'user',
            'street_address',
            'apartment_address',
            'country',
            'zip',
            'address_type',
            'default',
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id',
            'amount',
            'timestamp',
        )


class SearchItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id',
            'title',
            'price',
            'discount_price',
            'image',
            'category',
            'label',
            'description',
        )

    def get_category(self, obj):
        return obj.get_category_display()

    def get_price(self, obj):
        price = obj.price
        return "$ %s" % price

    def get_label(self, obj):
        return obj.get_label_display()


class SearchSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()

    def get_results(self, obj):
        return SearchItemSerializer(obj['results'], many=True).data

    def get_name(self, obj):
        return obj['name']
