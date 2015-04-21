from django.db import transaction
from shopping_cart_challenge.models import ProductQuantity, OrderStatus, Order


# noinspection PyMethodMayBeStatic
class OrderService:


    def create_new_order(self, product_quantities=None):

        with transaction.atomic():
            new_order = Order.objects.create(status=OrderStatus.EDIT)
            new_order.save()

            if product_quantities:
                self.update_prod_quantities(order=new_order, new_product_quantities=product_quantities)

        return new_order


    def update_prod_quantities(self, order, new_product_quantities):
        self._check_modification_allowed(order)
        if order.status != OrderStatus.EDIT:
            raise Exception('Action disallowed; Product quantities can be modified only for orders of status EDIT')


        with transaction.atomic():

            current_pq_dict = {}
            current_pq_objects = {}
            for pq in order.product_quantities():
                assert pq.product_id not in current_pq_dict, 'key collision'
                current_pq_dict[pq.product_id] = pq.quantity
                current_pq_objects[pq.product_id] = pq

            for prod_id in current_pq_dict:
                if prod_id in new_product_quantities:
                    # update changed product quantities, if applicable
                    curr_obj = current_pq_objects[prod_id]
                    new_quantity = new_product_quantities.pop(prod_id)
                    if curr_obj.quantity != new_quantity:
                        curr_obj.quantity = new_quantity
                        curr_obj.save()
                else:
                    # get rid of quantity records for products that are no longer applicable
                    current_pq_objects[prod_id].delete()

            # create quantity records for newly-added products
            for new_prod_id in new_product_quantities:
                new_pq_object = ProductQuantity.objects.create(
                    order_id=order.id,
                    product_id=new_prod_id,
                    quantity=new_product_quantities[new_prod_id],
                )
                new_pq_object.save()


    def set_status_edit(self, order):
        self._check_modification_allowed(order)
        order.status = OrderStatus.EDIT
        order.save()


    def set_status_review(self, order):
        self._check_modification_allowed(order)
        order.status = OrderStatus.REVIEW
        order.save()


    def set_status_confirmed(self, order):
        self._check_modification_allowed(order)

        if order.status != OrderStatus.REVIEW:
            raise Exception('Action disallowed - only order status REVIEW can be promoted to CONFIRMED')

        order.status = OrderStatus.CONFIRMED

        # TODO: generate confirmation number here
        # order.confirmation_number = ???

        order.save()



    def _check_modification_allowed(self, order):
        if order.status == OrderStatus.CONFIRMED:
            # TODO: raise proper exception type, that can be tied to a meaningful error code
            raise Exception("Modification disallowed: order is already confirmed")
