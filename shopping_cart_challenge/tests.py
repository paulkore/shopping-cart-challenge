from django.test import TestCase

from shopping_cart_challenge.models import Product, Order, ProductQuantity


class OrderModelTests(TestCase):

    @staticmethod
    def _createProduct(name, price):
        return

    def setUp(self):
        self.assertTrue(len(Product.objects.all()) == 0, 'Start with and empty database')
        self.assertTrue(len(Order.objects.all()) == 0, 'Start with and empty database')
        self.assertTrue(len(ProductQuantity.objects.all()) == 0, 'Start with and empty database')

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
