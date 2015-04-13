# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_cart_challenge', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('status', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'sc_order',
            },
        ),
        migrations.CreateModel(
            name='ProductQuantity',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('order', models.ForeignKey(to='shopping_cart_challenge.Order')),
                ('product', models.ForeignKey(to='shopping_cart_challenge.Product')),
            ],
            options={
                'db_table': 'sc_product_quantity',
            },
        ),
    ]
