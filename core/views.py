from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render
from .models import Order, OrderItem, Item
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


class HomeView(ListView):
    model = Item
    paginate_by = 2
    template_name = "home.html"


def home(request, *args, **kwargs):
    return render(request, 'home.html')


def product(request, *args, **kwargs):
    return render(request, 'product.html')


def checkout(request, *args, **kwargs):
    return render(request, 'checkout.html')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

    def get_context_data(self, **kwargs):
        addition_items = Item.objects.all()
        context = super().get_context_data(**kwargs)
        context['addition'] = addition_items
        return context


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    pre_delete_temp = False
    if order_item.pre_delete:
        order_item.pre_delete = False
        pre_delete_temp = True
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order_item in order
        if order.items.filter(item__slug=item.slug):
            if pre_delete_temp:
                order_item.quantity = 1
                order_item.save()
                messages.success(request, 'This item was added to your cart.')
                return redirect(request.META.get('HTTP_REFERER'))
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was updated.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            order.items.add(order_item)
            order.save()
            messages.success(request, 'This item was added to your cart.')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        time_add = timezone.now()
        order = Order.objects.create(user=request.user, time_add=time_add)
        order.items.add(order_item)
        order.save()
        messages.success(request, 'This item was added to your cart.')
        return redirect(request.META.get('HTTP_REFERER'))


def plus_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_item.quantity += 1
    order_item.save()
    messages.success(request, 'This item quantity was updated.')
    return redirect('core:order-summary')


def minus_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_item.quantity -= 1
    if order_item.quantity < 2:
        order_item.quantity = 1
        order_item.pre_delete = True
    order_item.save()
    messages.success(request, 'This item quantity was updated.')
    return redirect('core:order-summary')


def remove_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order_item in order
        if order.items.filter(item__slug=item.slug):
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            # need to know : can get rid of line below?
            order.items.remove(order_item)
            order.save()
            order_item.delete()
            messages.success(request, 'This item was removed from your cart')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'This item was not in your cart.')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.warning(request, 'You do not have an active order.')
        return redirect(request.META.get('HTTP_REFERER'))


def toggle_pre_delete_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    if not order_item.pre_delete:
        order_item.pre_delete = True
        order_item.save()
        messages.info(
            request, f'{order_item.item.title} status is pre-delete, you can undo on the right.')
        return redirect('core:order-summary')
    else:
        order_item.pre_delete = False
        order_item.save()
        messages.info(
            request, f'{order_item.item.title} status is active.')
        return redirect('core:order-summary')


# Create your views here.
