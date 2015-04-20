from django.http import Http404
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from shopping_cart_challenge.models import Product, Order
from shopping_cart_challenge.serializers import ProductSerializer, OrderReadSerializer, OrderWriteSerializer


def info_view(request):
    return render(request, 'info.html')


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer


class OrderAPIView(APIView):

    @staticmethod
    def _find_order(pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404
        return order

    @staticmethod
    def get(request, pk=None):
        if pk:
            order = OrderAPIView._find_order(pk)
        else:
            return Response({'order_id': None})

        serializer = OrderReadSerializer(order)
        return Response(serializer.data)

    @staticmethod
    def post(request, pk=None):

        if pk:
            # update existing order
            existing_order = OrderAPIView._find_order(pk)
            serializer = OrderWriteSerializer(existing_order, data=request.data)

        else:
            # create new order
            serializer = OrderWriteSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            order = serializer.save()
            return Response({'order_id': order.id})
        else:
            return Response({'error': 'invalid request data'})



