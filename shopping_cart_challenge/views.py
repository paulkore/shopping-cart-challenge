from django.shortcuts import render
from rest_framework import viewsets
from shopping_cart_challenge.models import Product
from shopping_cart_challenge.serializers import ProductSerializer


def info_view(request):
    return render(request, 'info.html')

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
