from django.db import models

# Create your models here.

class Product(models.Model):
    DELIVERY_CHOICES = [
        ('Full', 'Full'),
        ('Normal', 'Normal'),
    ]

    name = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField(null=True, blank=True)
    installment = models.CharField(max_length=200, null=True, blank=True)
    image_url = models.URLField(max_length=1000)
    product_url = models.URLField(max_length=1000)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    free_shipping = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name