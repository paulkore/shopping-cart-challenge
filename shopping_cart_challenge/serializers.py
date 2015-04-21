from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from shopping_cart_challenge.models import Product, OrderStatus
from shopping_cart_challenge.services import OrderService


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price')


# noinspection PyAbstractClass
class OrderReadSerializer(serializers.BaseSerializer):

    def to_representation(self, order):
        product_quantities = order.product_quantities()

        serialized_order = {
            'order_id': order.id,
            'order_status': OrderStatus.to_str(order.status),
            'order_total': Decimal(0),
            'products': []
        }
        for pq in product_quantities:
            serialized_order['products'].append({
                'quantity': pq.quantity,
                'product': ProductSerializer(pq.product).data
            })
            serialized_order['order_total'] += pq.product.price * pq.quantity

        return serialized_order




# noinspection PyAbstractClass
class ProductQuantityWriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


# noinspection PyAbstractClass, PyMethodMayBeStatic
class OrderWriteSerializer(serializers.Serializer):
    order_status = serializers.ChoiceField(choices=OrderStatus.all_values_str())
    product_quantities = ProductQuantityWriteSerializer(many=True, required=False, allow_null=True)


    # def __init__(self, *args, **kwargs):
    #     super(OrderWriteSerializer, self).__init__(args, kwargs)
    #     self.order_service = OrderService()

    def _extract_order_status(self, validated_data):
        order_status_str = validated_data.get('order_status')
        order_status = OrderStatus.from_str(order_status_str)
        return order_status


    def _extract_prod_quantities(self, validated_data):
        pq_data = validated_data.get('product_quantities')
        pq_dict = {}
        for pq in pq_data:
            product_id = pq['product_id']
            quantity = pq['quantity']

            assert product_id not in pq_dict, 'key collision'
            pq_dict[product_id] = quantity

        return pq_dict


    def create(self, validated_data):
        # TODO: make this an instance variable
        order_service = OrderService()

        prod_quantities = self._extract_prod_quantities(validated_data)
        new_order = order_service.create_new_order(product_quantities=prod_quantities)
        return new_order


    def update(self, instance, validated_data):
        # TODO: make this an instance variable
        order_service = OrderService()

        order_status = self._extract_order_status(validated_data)
        prod_quantities = self._extract_prod_quantities(validated_data)

        with transaction.atomic():
            if order_status == OrderStatus.EDIT:
                order_service.set_status_edit(instance)

            elif order_status == OrderStatus.REVIEW:
                order_service.update_prod_quantities(instance, new_product_quantities=prod_quantities)
                order_service.set_status_review(instance)

            elif order_status == OrderStatus.CONFIRMED:
                order_service.set_status_confirmed(instance)

            else:
                raise Exception('Unhandled enum value: ' + str(order_status))

        return instance







