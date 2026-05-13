from django.shortcuts import render,redirect,get_object_or_404
from .models import Order, Product
from django.db.models import Q, Case, When, IntegerField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import OrderForm
from django.contrib.auth.decorators import login_required



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


# ORDER (ONLY LOGIN USERS CAN ACCESS)
@login_required(login_url='login')

def order_list(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.product_name = product
            order.price = product.price
            order.save()

            return redirect('dashboard')
    else:
        form = OrderForm()

    return render(request, 'order.html', {
        'product': product,
        'form': form
    })





# SIGNUP
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})




@login_required(login_url='login')
@login_required(login_url='login')
def dashboard(request):
    # ONLY ACTIVE ORDERS (NOT CANCELLED)
    orders = Order.objects.filter(
        user=request.user,
        status="pending"
    ).order_by('-order_date')

    # TOTAL ONLY FROM ACTIVE ORDERS
    total_amount = sum(order.price * order.quantity for order in orders)

    order_count = orders.count()

    return render(request, 'dashboard.html', {
        'orders': orders,
        'total_amount': total_amount,
        'order_count': order_count,
    })

@login_required(login_url='login')
def cancel_order(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)

    if order.status != "cancelled":
        order.status = "cancelled"
        order.save()

    return redirect('dashboard')
