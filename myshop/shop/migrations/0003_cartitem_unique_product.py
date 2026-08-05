from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0002_cart_cartitem_order_orderitem'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='cartitem',
            constraint=models.UniqueConstraint(
                fields=('cart', 'product'),
                name='unique_product_in_cart',
            ),
        ),
    ]
