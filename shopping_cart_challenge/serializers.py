from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from shopping_cart_challenge.models import Product, OrderStatus, Order, ProductQuantity


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


# noinspection PyAbstractClass
class OrderWriteSerializer(serializers.Serializer):
    order_status = serializers.ChoiceField(choices=OrderStatus.all_values_str())
    product_quantities = ProductQuantityWriteSerializer(many=True, required=False, allow_null=True)


    def _sync_product_quantities(self, order, prod_quantities_data):
        current_pq_dict = {}
        current_pq_objects = {}
        for pq in order.product_quantities():
            assert pq.product_id not in current_pq_dict, 'key collision'
            current_pq_dict[pq.product_id] = pq.quantity
            current_pq_objects[pq.product_id] = pq

        new_pq_dict = {}
        for pq in prod_quantities_data:
            assert pq['product_id'] not in new_pq_dict, 'key collision'
            new_pq_dict[pq['product_id']] = pq['quantity']


        for prod_id in current_pq_dict:
            if prod_id in new_pq_dict:
                # update changed product quantities, if applicable
                curr_obj = current_pq_objects[prod_id]
                new_quantity = new_pq_dict.pop(prod_id)
                if curr_obj.quantity != new_quantity:
                    curr_obj.quantity = new_quantity
                    curr_obj.save()
            else:
                # get rid of quantity records for products that are no longer applicable
                current_pq_objects[prod_id].delete()

        # create quantity records for newly-added products
        for new_prod_id in new_pq_dict:
            new_pq_object = ProductQuantity.objects.create(
                order_id=order.id,
                product_id=new_prod_id,
                quantity=new_pq_dict[new_prod_id],
            )
            new_pq_object.save()


    def create(self, validated_data):
        with transaction.atomic():
            new_order = Order.objects.create(status=OrderStatus.REVIEW)
            new_order.save()

            pq_data = validated_data.get('product_quantities')
            self._sync_product_quantities(new_order, pq_data)

        return new_order


    def update(self, instance, validated_data):
        status_str = validated_data.get('order_status', instance.status)
        status = OrderStatus.from_str(status_str)

        with transaction.atomic():

            if status == OrderStatus.EDIT or status == OrderStatus.CONFIRMED:
                instance.status = status
                instance.save()

            elif status == OrderStatus.REVIEW:
                instance.status = status
                instance.save()

                pq_data = validated_data.get('product_quantities')
                self._sync_product_quantities(instance, pq_data)

            elif status == OrderStatus.CONFIRMED:
                instance.status = status
                instance.save()

                # TODO: generate confirmation number

            else:
                raise Exception('Unhandled enum value: ' + str(status))

        return instance







