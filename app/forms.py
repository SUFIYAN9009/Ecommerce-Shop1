from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'email', 'phone', 'quantity', 'address']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'p-3 border rounded-xl w-full focus:ring-2 focus:ring-black'
            })