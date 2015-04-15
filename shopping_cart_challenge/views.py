from django.http import Http404
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from shopping_cart_challenge.models import Product, Order, OrderStatus
from shopping_cart_challenge.serializers import ProductSerializer


def info_view(request):
    return render(request, 'info.html')


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer


class OrderDetail(APIView):

    @staticmethod
    def get_object(pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        order = self.get_object(pk)
        product_quantities = order.product_quantities()

        response_data = {}
        response_data['order_id'] = order.id
        response_data['order_status'] = OrderStatus.to_str(order.status)
        pq_list = []
        for pq in product_quantities:
            pq_list.append({
                'quantity': pq.quantity,
                'product': ProductSerializer(pq.product).data
            })
        response_data['products'] = pq_list

        return Response(response_data)

