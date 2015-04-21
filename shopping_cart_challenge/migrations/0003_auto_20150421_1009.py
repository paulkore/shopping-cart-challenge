# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_cart_challenge', '0002_order_productquantity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productquantity',
            options={'verbose_name_plural': 'product quantities'},
        ),
        migrations.AddField(
            model_name='order',
            name='confirmation_number',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
