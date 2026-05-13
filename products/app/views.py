from django.shortcuts import render,redirect,get_object_or_404
from .models import Order, Product
from django.db.models import Q, Case, When, IntegerField




# Create your views here.

def home(request):
     products = Product.objects.all()
     return render(request, 'home.html', {'products': products}) 
   

def header_footer(request):
    return render(request, 'header_footer.html')

def about(request):
    return render(request, 'about.html')    

def service(request):
    return render(request, 'service.html')  



def product_list(request):

    query = request.GET.get('q')

    products = Product.objects.all()

    if query:
        products = products.annotate(
            relevance=Case(
                When(name__icontains=query, then=3),
                When(description__icontains=query, then=2),
                default=1,
                output_field=IntegerField()
            )
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).order_by('-relevance')

    return render(request, 'product.html', {
        'products': products,
        'query': query
    })


def order_list(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        Order.objects.create(
            customer_name=request.POST.get('customer_name'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            product_name=product,
            price=product.price,
            quantity=request.POST.get('quantity')
        )
        return redirect('home')

    return render(request, 'order.html', {'product': product})

