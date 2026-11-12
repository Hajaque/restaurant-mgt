# Import Django form tools
from django import forms
from django.forms import inlineformset_factory

# Import existing restaurant models
from restuarant.models import Order, OrderItem, MenuItem


# =====================================================
# ORDER FORM
# =====================================================

class OrderForm(forms.ModelForm):

    class Meta:

        # Connect this form to the existing Order model
        model = Order

        # Fields the user will fill in
        fields = [
            'customer_name',
            'table_number',
        ]

        # Customize the appearance of form fields
        widgets = {

            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),

            'table_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter table number',
                'min': '1'
            }),
        }


# =====================================================
# ORDER ITEM FORM
# =====================================================

class OrderItemForm(forms.ModelForm):

    class Meta:

        model = OrderItem

        # The user selects a menu item and its quantity
        fields = [
            'menu_item',
            'quantity',
        ]

        widgets = {

            'menu_item': forms.Select(attrs={
                'class': 'form-control'
            }),

            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }


# =====================================================
# ORDER ITEM FORMSET
# =====================================================

# This allows us to add multiple menu items to one order.
# Each order can contain several different items.

OrderItemFormSet = inlineformset_factory(

    Order,

    OrderItem,

    form=OrderItemForm,

    extra=1,

    can_delete=True

)