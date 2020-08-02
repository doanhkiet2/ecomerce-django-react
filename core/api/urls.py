from django.urls import path
from .views import (
    ItemListView,
    AddToCartView,
    OrderDetailView,
    ItemDetailView,
    AddressListView,
    AddressCreateView,
    CountryListView,
    UserIDView,
    AddressUpdateView,
    AddressDestroyView,
    OrderQuantityMinusItem,
    SearchView,
    DesignerDetailView,
)

from orders.api.views import AddCouponView, PaymentView, PaymentListView
from core.api.views import OrderDeleteView

urlpatterns = [
    path('user-id/', UserIDView.as_view(), name='user-id'),
    path('products/', ItemListView.as_view(), name='product-list'),

    path('searcha/', SearchView.as_view(), name='searcha'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('products/<pk>/', ItemDetailView.as_view(), name='product-detail'),
    path('designer/<pk>', DesignerDetailView.as_view(), name='designer-detail'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('checkout/', PaymentView.as_view(), name='checkout'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('addresses/', AddressListView.as_view(), name='address-list'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('addresses/create/', AddressCreateView.as_view(), name='address-create'),
    path('addresses/<pk>/update/',
         AddressUpdateView.as_view(), name='address-update'),
    path('addresses/<pk>/delete/',
         AddressDestroyView.as_view(), name='address-delete'),
    path('order-items/<pk>/delete/',
         OrderDeleteView.as_view(), name='order-item-delete'),
    path('order-items/minus-quantity/',
         OrderQuantityMinusItem.as_view(), name='order-items-minus-quantity'),



]
