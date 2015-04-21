from django.test import TestCase
from django.utils import unittest

from shopping_cart_challenge.models import Product, Order, ProductQuantity, OrderStatus
from shopping_cart_challenge.services import OrderService


class OrderTestHelper:

    @staticmethod
    def get_product_quantities_as_dict(order):
        pq_dict = {}
        for pq in order.product_quantities():
            pq_dict[pq.product_id] = pq.quantity
        return pq_dict


class OrderModelTests(TestCase):

    def setUp(self):
        self.assertTrue(len(Product.objects.all()) == 0, 'Start with empty db')
        self.assertTrue(len(Order.objects.all()) == 0, 'Start with empty db')
        self.assertTrue(len(ProductQuantity.objects.all()) == 0, 'Start with empty db')




    def test_product_quantities_empty_order(self):
        Product.objects.create(name='product1', price=10.00)
        Product.objects.create(name='product2', price=5.75)
        self.assertTrue(len(Product.objects.all()) == 2, 'records saved')

        order1 = Order.objects.create()
        order2 = Order.objects.create()
        self.assertTrue(len(Order.objects.all()) == 2, 'records saved')
        self.assertTrue(order1.id != order2.id, 'different orders')

        prod_quantities1 = order1.product_quantities()
        prod_quantities2 = order2.product_quantities()

        self.assertTrue(len(prod_quantities1) == 0, 'order 1 is empty, no product quantities')
        self.assertTrue(len(prod_quantities2) == 0, 'order 2 is empty, no product quantities')

    def test_product_quantities_non_empty_order(self):
        product1 = Product.objects.create(name='product1', price=10.00)
        product2 = Product.objects.create(name='product2', price=5.75)
        self.assertTrue(len(Product.objects.all()) == 2, 'records saved')

        order1 = Order.objects.create()
        order2 = Order.objects.create()
        self.assertTrue(len(Order.objects.all()) == 2, 'records saved')
        self.assertTrue(order1.id != order2.id, 'different orders')

        ProductQuantity.objects.create(order=order2, product=product1, quantity=5)
        ProductQuantity.objects.create(order=order2, product=product2, quantity=22)

        prod_quantities1 = order1.product_quantities()
        prod_quantities2 = order2.product_quantities()

        self.assertTrue(len(prod_quantities1) == 0, 'order 1 is empty, no product quantities')
        self.assertTrue(len(prod_quantities2) == 2, 'order 2 is not empty, found product quantities')
        self.assertEquals(prod_quantities2[0].quantity, 5, 'checking quantity of product 1')
        self.assertEquals(prod_quantities2[1].quantity, 22, 'checking quantity of product 2')



class OrderServiceTests(TestCase):

    def setUp(self):
        self.assertTrue(len(Product.objects.all()) == 0, 'Start with empty db')
        self.assertTrue(len(Order.objects.all()) == 0, 'Start with empty db')
        self.assertTrue(len(ProductQuantity.objects.all()) == 0, 'Start with empty db')

        self.product1 = Product.objects.create(name='product1', price=10.00)
        self.product2 = Product.objects.create(name='product2', price=5.75)
        self.product3 = Product.objects.create(name='product3', price=24.99)
        self.assertTrue(len(Product.objects.all()) == 3, 'records saved')

        self.service = OrderService()


    def test_create_new_order_basic(self):

        order = self.service.create_new_order()

        self.assertIsNotNone(order, 'order object was returned')
        self.assertTrue(len(Order.objects.all()) == 1, 'order record was created in db')
        self.assertEquals(order.id, Order.objects.all()[0].id, 'order id matches the one on db record')
        self.assertEquals(order.status, OrderStatus.EDIT, 'order status is EDIT when created')
        self.assertTrue(len(order.product_quantities()) == 0, 'order has no product quantities yet')


    def test_create_new_order_with_prod_quantities(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }

        order = self.service.create_new_order(product_quantities=prod_quantities)

        self.assertIsNotNone(order, 'order object was returned')
        self.assertTrue(len(Order.objects.all()) == 1, 'order record was created in db')
        self.assertEquals(order.id, Order.objects.all()[0].id, 'order id matches the one on db record')
        self.assertEquals(order.status, OrderStatus.EDIT, 'order status is EDIT when created')

        pq_data = OrderTestHelper.get_product_quantities_as_dict(order)

        self.assertEquals(len(pq_data), 2, 'product quantity record count matches')
        self.assertTrue(self.product1.id in pq_data, '1st product id matches')
        self.assertTrue(self.product3.id in pq_data, '3rd product id matches')

        self.assertEquals(pq_data[self.product1.id], 5, '1st product quantity matches')
        self.assertEquals(pq_data[self.product3.id], 12, '3rd product quantity matches')


    def test_update_product_quantities_modify(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)

        new_prod_quantities = {
            self.product1.id: 7,
            self.product3.id: 22,
        }

        self.service.update_prod_quantities(order, new_prod_quantities)

        pq_data = OrderTestHelper.get_product_quantities_as_dict(order)

        self.assertEquals(len(pq_data), 2, 'product quantity record count matches')
        self.assertTrue(self.product1.id in pq_data, '1st product id matches')
        self.assertTrue(self.product3.id in pq_data, '3rd product id matches')

        self.assertEquals(pq_data[self.product1.id], 7, '1st product quantity matches')
        self.assertEquals(pq_data[self.product3.id], 22, '3rd product quantity matches')


    def test_update_product_quantities_add_new(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)

        new_prod_quantities = {
            self.product1.id: 5,
            self.product2.id: 3,
            self.product3.id: 12,
        }

        self.service.update_prod_quantities(order, new_prod_quantities)

        pq_data = OrderTestHelper.get_product_quantities_as_dict(order)

        self.assertEquals(len(pq_data), 3, 'product quantity record count matches')
        self.assertTrue(self.product1.id in pq_data, '1st product id matches')
        self.assertTrue(self.product2.id in pq_data, '2nd product id matches')
        self.assertTrue(self.product3.id in pq_data, '3rd product id matches')

        self.assertEquals(pq_data[self.product1.id], 5, '1st product quantity matches')
        self.assertEquals(pq_data[self.product2.id], 3, '2nd product quantity matches')
        self.assertEquals(pq_data[self.product3.id], 12, '3rd product quantity matches')


    def test_update_product_quantities_remove(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)

        new_prod_quantities = {
            self.product3.id: 12,
        }

        self.service.update_prod_quantities(order, new_prod_quantities)

        pq_data = OrderTestHelper.get_product_quantities_as_dict(order)

        self.assertEquals(len(pq_data), 1, 'product quantity record count matches')
        self.assertTrue(self.product3.id in pq_data, '3rd product id matches')

        self.assertEquals(pq_data[self.product3.id], 12, '3rd product quantity matches')


    def test_update_product_quantities_disallowed_in_review(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)
        self.service.set_status_review(order)

        new_prod_quantities = {
            self.product1.id: 5,
            self.product2.id: 3,
            self.product3.id: 12,
        }

        with self.assertRaisesRegexp(Exception, 'Action disallowed'):
            self.service.update_prod_quantities(order, new_prod_quantities)


    def test_set_status_edit_to_review(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }

        order = self.service.create_new_order(product_quantities=prod_quantities)
        self.assertEquals(order.status, OrderStatus.EDIT, 'order status is EDIT when created')

        self.service.set_status_review(order)
        self.assertEquals(order.status, OrderStatus.REVIEW, 'order status changed to REVIEW')


    @unittest.skip("functionality not ready")
    def test_set_status_edit_to_review_generates_order_total(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }

        order = self.service.create_new_order(product_quantities=prod_quantities)
        self.assertEquals(order.total, None, 'order total is undefined on new order')

        self.service.set_status_review(order)
        expected_total = self.product1.price * 5 + self.product3.price * 12
        self.assertTrue(expected_total > 0, 'expected total is greater than zero')
        self.assertEquals(order.total, expected_total, 'order total matches expected total')


    def test_set_status_review_back_to_edit(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }

        order = self.service.create_new_order(product_quantities=prod_quantities)
        self.service.set_status_review(order)
        self.assertEquals(order.status, OrderStatus.REVIEW, 'order status is REVIEW')

        self.service.set_status_edit(order)
        self.assertEquals(order.status, OrderStatus.EDIT, 'order status changed back to EDIT')


    def test_set_status_edit_to_confirmed_disallowed(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)

        with self.assertRaisesRegexp(Exception, 'Action disallowed'):
            self.service.set_status_confirmed(order)


    def test_set_status_review_to_confirmed(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)

        self.service.set_status_review(order)
        self.assertEquals(order.status, OrderStatus.REVIEW, 'order status is REVIEW')

        self.service.set_status_confirmed(order)
        self.assertEquals(order.status, OrderStatus.CONFIRMED, 'order status changed to CONFIRMED')


    @unittest.skip("functionality not ready")
    def test_set_status_confirmed_generates_confirmation_number(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)

        self.assertIsNone(order.confirmation_number, 'confirmation number undefined on new order')
        self.service.set_status_review(order)
        self.assertIsNone(order.confirmation_number, 'confirmation number undefined on order in review')
        self.service.set_status_confirmed(order)
        self.assertIsNotNone(order.confirmation_number, 'confirmation number is set on confirmed order')
        self.assertRegexpMatches(order.confirmation_number, "^[0-9a-zA-Z]{6}$", 'confirmation number is in expected format')


    def test_confirmed_order_cant_change_status(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)
        self.service.set_status_review(order)
        self.service.set_status_confirmed(order)

        with self.assertRaisesRegexp(Exception, 'Modification disallowed'):
            self.service.set_status_review(order)

        with self.assertRaisesRegexp(Exception, 'Modification disallowed'):
            self.service.set_status_edit(order)


    def test_confirmed_order_cant_modify_product_quantities(self):
        prod_quantities = {
            self.product1.id: 5,
            self.product3.id: 12,
        }
        order = self.service.create_new_order(product_quantities=prod_quantities)
        self.service.set_status_review(order)
        self.service.set_status_confirmed(order)


        new_prod_quantities = {
            self.product1.id: 5,
            self.product2.id: 3,
            self.product3.id: 12,
        }

        with self.assertRaisesRegexp(Exception, 'Modification disallowed'):
            self.service.update_prod_quantities(order, new_prod_quantities)







