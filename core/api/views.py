from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.models import Designer, Item, ItemVariation, Order, OrderItem, Variation
from .serializers import ItemSerializer
from django.contrib import messages
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from core.api.serializers import AddressSerializer, DesignerDetailSerializer, ItemDetailSerializer, OrderSerializer, SearchSerializer
from django.core.exceptions import ObjectDoesNotExist
from orders.models import Address

from django.http import Http404
from django_countries import countries
from django.shortcuts import get_object_or_404
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q
from django.contrib.postgres.aggregates.general import StringAgg
from functools import reduce
import operator


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'userID': request.user.id}, status=HTTP_200_OK)


class ItemListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemDetailSerializer
    queryset = Item.objects.all()


class ItemDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemDetailSerializer
    queryset = Item.objects.all()


class DesignerDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = DesignerDetailSerializer
    queryset = Designer.objects.all()


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        item_variations = request.data.get('item_variations', [])
        if slug is None:
            return Response({'message': 'Invalid Request'}, HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)

        minimum_variation_count = Variation.objects.filter(item=item).count()
        if len(item_variations) < minimum_variation_count:
            return Response({'message': 'please specify the required variations.'}, HTTP_400_BAD_REQUEST)

        order_item_qs = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False
        )
        for iv in item_variations:
            order_item_qs = order_item_qs.filter(
                item_variations__exact=iv
            )

        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()

        else:
            order_item = OrderItem.objects.create(
                item=item,
                user=request.user,
                ordered=False
            )
            order_item.item_variations.add(*item_variations)
            order_item.save()

        pre_delete_temp = False
        if order_item.pre_delete:
            order_item.pre_delete = False
            # pre_delete_temp = True

        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if order_item in order
            # if order.items.filter(item__slug=item.slug):
            # if pre_delete_temp:
            #     order_item.quantity = 1
            #     order_item.save()
            #     # messages.success(
            #     #     request, 'This item was added to your cart.')
            #     return Response(status=HTTP_200_OK)
            # order_item.quantity += 1
            # order_item.save()
            # # messages.info(request, 'This item quantity was updated.')
            # return Response(status=HTTP_200_OK)

            if not order.items.filter(item__id=order_item.id).exists():
                order.items.add(order_item)
                order.save()
                # messages.success(request, 'This item was added to your cart.')
            return Response(status=HTTP_200_OK)

        else:
            time_add = timezone.now()
            order = Order.objects.create(user=request.user, time_add=time_add)
            order.items.add(order_item)
            order.save()
            # messages.success(request, 'This item was added to your cart.')
            return Response(status=HTTP_200_OK)


class OrderQuantityMinusItem(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        item_variations = request.data.get('item_variations', [])
        if slug is None:
            return Response({"message": "Ivalid data"}, status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]

            minimum_variation_count = Variation.objects.filter(
                item=item).count()
            if len(item_variations) < minimum_variation_count:
                return Response({'message': 'please specify the required variations.'}, HTTP_400_BAD_REQUEST)

            # check if order_item in order
            order_item_qs = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )
            for iv in item_variations:
                order_item_qs = order_item_qs.filter(
                    item_variations__exact=iv
                )
            if not order_item_qs.exists():
                return Response({"message": "This (variations) item is not exist or not in your cart"}, status=HTTP_400_BAD_REQUEST)
            order_item = order_item_qs[0]
            if order_item in order.items.all():
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                    order.save()
                    order_item.delete()
                return Response({"message": "successful"}, status=HTTP_200_OK)

            else:
                return Response({"message": "This (variations) item is not in your cart"}, status=HTTP_400_BAD_REQUEST)

        else:
            return Response({"message": "No order active"}, status=HTTP_400_BAD_REQUEST)


class OrderDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = OrderItem.objects.all()


class OrderDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    # permission_classes = (AllowAny,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            print('false')
            raise Http404("You do not have an active order")
            # return Response({'message': 'you do not have active order'}, status=HTTP_400_BAD_REQUEST)


class CountryListView(APIView):
    def get(self, request, *args, **kwargs):
        print(countries)
        return Response(countries, status=HTTP_200_OK)


class AddressListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer

    def get_queryset(self):
        address_type = self.request.query_params.get('address_type', None)
        qs = Address.objects.all()
        if address_type is None:
            return qs
        return qs.filter(user=self.request.user, address_type=address_type.upper()).order_by('-time_add')


class AddressCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressDestroyView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


# def get_search_value(data):
#     # sv = data.get('sv')
#     sv_ser = SearchSerializer(data or None)
#     sv = sv_ser.cleandata

class SearchView(ListAPIView):
    permission_classes = (AllowAny,)
    # serializer_class = ItemSerializer
    serializer_class = SearchSerializer

    def get_queryset(self):
        s_value = self.request.query_params.get('s_value')
        s_split_vlue = s_value.split(' ')
        print(s_value)

        # qs1 = Item.objects.annotate(
        #     search=SearchVector(StringAgg('tags__name', delimiter=' '), 'title'),).filter(search__contains=s_value)
        # qsd=SearchVector('title', weight='A'), search2=SearchVector(
        #     'description', weight='B')).filter(Q(search1__icontains=s_value) | Q(search2__icontains=s_value))
        # print(qs1)
        vector = SearchVector('title', weight='A') + \
            SearchVector(StringAgg('description', delimiter=''), weight='B')
        query = SearchQuery("TOKNOW")
        qs1 = Item.objects\
            .annotate(document=vector, rank=SearchRank(vector, query))\
            .filter(reduce(operator.and_, (Q(document__icontains=x) for x in s_split_vlue)))\
            .order_by('-rank')\
            # .filter((Q(document__icontains="we") & Q(document__icontains="your")))\

        def new(label):
            name = label
            results = qs1.filter(label=label)
            return dict(name=name, results=results)
        qs = list(map(new, ["P", "S", "D"]))
        print(qs)

        return qs
