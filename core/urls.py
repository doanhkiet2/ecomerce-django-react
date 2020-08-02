from django.urls import path
from .views import (
    minus_item,
    plus_item,
    remove_item_from_cart,
    add_item_to_cart,
    OrderSummaryView,
    toggle_pre_delete_item,
    HomeView,
    ItemDetailView,

)

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>', ItemDetailView.as_view(), name='product'),
    path('order-summary', OrderSummaryView.as_view(), name='order-summary'),
    path('minus-item/<slug>', minus_item, name='minus-item'),
    path('plus-item/<slug>', plus_item, name='plus-item'),
    path('remove-item-from-cart/<slug>', remove_item_from_cart,
         name='remove-item-from-cart'),
    path('add-item-to-cart/<slug>', add_item_to_cart, name='add-item-to-cart'),
    path('toggle-pre-delete-item/<slug>',
         toggle_pre_delete_item, name='toggle-pre-delete-item'),


]
