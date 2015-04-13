from rest_framework import serializers
from shopping_cart_challenge.models import Product


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('url', 'id', 'name', 'price')

