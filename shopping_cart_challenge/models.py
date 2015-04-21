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
    EDIT = 1
    REVIEW = 2
    CONFIRMED = 3

    _str_to_val = {
        'EDIT': EDIT,
        'REVIEW': REVIEW,
        'CONFIRMED': CONFIRMED,
    }

    _val_to_str = {
        EDIT: 'EDIT',
        REVIEW: 'REVIEW',
        CONFIRMED: 'CONFIRMED',
    }

    @staticmethod
    def all_values_str():
        return ['EDIT', 'REVIEW', 'CONFIRMED']

    @staticmethod
    def to_str(val):
        if val in OrderStatus._val_to_str:
            return OrderStatus._val_to_str[val]
        raise Exception('invalid enum value: ' + str(val))

    @staticmethod
    def from_str(str):
        if str in OrderStatus._str_to_val:
            return OrderStatus._str_to_val[str]
        raise Exception('invalid enum value: ' + str)





class Order(models.Model):
    status = enum.EnumField(OrderStatus, default=OrderStatus.EDIT)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    confirmation_number = models.CharField(max_length=50, null=True, blank=False)

    class Meta:
        db_table = 'sc_order'

    def __str__(self):
        return "Order (id: %d)" % self.id

    def product_quantities(self):
        return ProductQuantity.objects.filter(order_id=self.id).order_by('id')



class ProductQuantity(models.Model):
    class Meta:
        db_table = 'sc_product_quantity'
        verbose_name_plural = "product quantities"

    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()

    def __str__(self):
        return "Order (id: %d) --- %d x \"%s\"" % (self.order_id, self.quantity, self.product.name)