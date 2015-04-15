from decimal import Decimal
from django.http import Http404
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from shopping_cart_challenge.models import Product, Order, OrderStatus
from shopping_cart_challenge.serializers import ProductSerializer


def info_view(request):
    return render(request, 'info.html')



#
#  API views are below
#

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer


class ExistingOrderAPIView(APIView):

    @staticmethod
    def get(request, pk, format=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

        product_quantities = order.product_quantities()

        response_data = {
            'order_id': order.id,
            'order_status': OrderStatus.to_str(order.status),
            'order_total': Decimal(0),
            'products': []
        }
        for pq in product_quantities:
            response_data['products'].append({
                'quantity': pq.quantity,
                'product': ProductSerializer(pq.product).data
            })
            response_data['order_total'] += pq.product.price * pq.quantity

        return Response(response_data)

