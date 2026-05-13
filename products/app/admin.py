from django.contrib import admin
from .models import Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','description','price','image','stock']  
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): 
    list_display = ['customer_name','email','phone','address','product_name','price','quantity','order_date']         