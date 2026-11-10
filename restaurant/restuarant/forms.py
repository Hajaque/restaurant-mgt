# Import Django's ModelForm and forms modules
from django import forms

# Import our MenuItem model
from .models import MenuItem


# ModelForm automatically creates form fields from our model.
# This saves us from writing every form field manually.
class MenuItemForm(forms.ModelForm):

    class Meta:
        # Specify the model that this form will work with
        model = MenuItem

        # Specify the fields that users are allowed to enter
        fields = [
            'name',
            'description',
            'category',
            'price',
            'is_available'
        ]

        # Customize how the form fields appear in HTML
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter menu item name'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item description',
                'rows': 4
            }),

            'category': forms.Select(attrs={
                'class': 'form-control'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price',
                'step': '0.01',
                'min': '0'
            }),

            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }