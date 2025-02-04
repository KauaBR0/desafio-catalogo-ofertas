from django.shortcuts import render

# Create your views here.
from .models import Product
from django.db.models import Max, Min, F

def product_list(request):
    products = Product.objects.all()
    
    if request.GET.get('free_shipping'):
        products = products.filter(free_shipping=True)
    if request.GET.get('full_delivery'):
        products = products.filter(delivery_type='Full')
    
    highlights = {
        'max_price': products.aggregate(Max('price'))['price__max'],
        'min_price': products.aggregate(Min('price'))['price__min'],
        'max_discount': products.exclude(discount_percentage=None)
                             .aggregate(Max('discount_percentage'))['discount_percentage__max']
    }
    
    return render(request, 'catalog/index.html', {
        'products': products,
        'highlights': highlights
    })