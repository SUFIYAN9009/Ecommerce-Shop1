from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
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
            return redirect('login')
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

@staff_member_required
def admin_dashboard(request):

    # get all orders
    orders = Order.objects.all().order_by('-order_date')

    # search
    query = request.GET.get('q')

    if query:
        orders = orders.filter(
            customer_name__icontains=query
        )

    # total orders
    total_orders = Order.objects.count()

    # total revenue
    total_revenue = Order.objects.aggregate(
        Sum('price')
    )['price__sum']

    return render(request, 'admin_dashboard.html', {

        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue,

    })

@staff_member_required
def update_order_status(request, id, status):

    order = get_object_or_404(Order, id=id)

    order.status = status
    order.save()

    return redirect('admin_dashboard')

@staff_member_required
def delete_order(request, id):

    order = get_object_or_404(Order, id=id)
    order.delete()

    return redirect('admin_dashboard')


@staff_member_required
def add_product(request):

    if request.method == "POST":

        name = request.POST['name']
        price = request.POST['price']
        stock = request.POST['stock']
        description = request.POST['description']
        image = request.FILES.get('image')  # ✅ IMPORTANT

        Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description,
            image=image
        )

        return redirect('product_list')

    return render(request, 'add_product.html')

@staff_member_required
def product_list(request):

    products = Product.objects.all().order_by('-id')

    return render(request, 'product_list.html', {
        'products': products
    })

@staff_member_required
def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        product.name = request.POST['name']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.description = request.POST['description']

        # ✅ update image only if new one uploaded
        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()

        return redirect('product_list')

    return render(request, 'edit_product.html', {
        'product': product
    })

@staff_member_required
def delete_product(request, id):

    product = get_object_or_404(Product, id=id)
    product.delete()

    return redirect('product_list')

def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)

    order.status = 'cancelled'
    order.save()

    return redirect('dashboard')

def my_orders(request):
    orders = Order.objects.filter(user=request.user)

    return render(request, 'orders/my_orders.html', {
        'orders': orders
    })