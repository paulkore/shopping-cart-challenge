from django.db import models
from django_enumfield import enum

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'sc_product'

    def __str__(self):
        return self.name



class OrderStatus(enum.Enum):
    STARTED = 1
    REVIEW = 2
    CONFIRMED = 3

class Order(models.Model):
    status = enum.EnumField(OrderStatus, default=OrderStatus.STARTED)

    class Meta:
        db_table = 'sc_order'

    def __str__(self):
        return "Order (id: %d)" % self.id

    def product_quantities(self):
        return ProductQuantity.filter(order_id=self.id).order_by('id')



class ProductQuantity(models.Model):
    class Meta:
        db_table = 'sc_product_quantity'
        verbose_name_plural = "product quantities"

    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()

    def __str__(self):
        return "Order (id: %d) --- %d x \"%s\"" % (self.order_id, self.quantity, self.product.name)