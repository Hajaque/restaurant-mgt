# Import Django functions
from django.shortcuts import render, redirect, get_object_or_404

# Import messages for notifications
from django.contrib import messages

# Import existing restaurant models
from restuarant.models import Order, MenuItem

# Import our order forms
from .forms import OrderForm, OrderItemFormSet


# =====================================================
# 1. DISPLAY ALL ORDERS
# =====================================================

def order_list(request):

    # Retrieve all orders, newest first
    orders = Order.objects.all().order_by('-created_at')

    context = {
        'orders': orders
    }

    return render(request, 'orders/order_list.html', context)


# =====================================================
# 2. CREATE A NEW ORDER
# =====================================================

def create_order(request):

    if request.method == 'POST':

        # Collect order information
        order_form = OrderForm(request.POST)

        # Check whether the order information is valid
        if order_form.is_valid():

            # Save the order temporarily
            order = order_form.save(commit=False)

            # Save the main order first so it has a database ID
            order.save()

            # Create the formset for the order items
            item_formset = OrderItemFormSet(
                request.POST,
                instance=order
            )

            # Validate the selected items
            if item_formset.is_valid():

                # Process each selected menu item
                for item_form in item_formset:

                    # Ignore empty forms and deleted forms
                    if not item_form.cleaned_data:
                        continue

                    if item_form.cleaned_data.get('DELETE'):
                        continue

                    # Get the selected menu item
                    menu_item = item_form.cleaned_data['menu_item']

                    # Get the requested quantity
                    quantity = item_form.cleaned_data['quantity']

                    # Prevent ordering unavailable items
                    if not menu_item.is_available:
                        order.delete()

                        messages.error(
                            request,
                            f'{menu_item.name} is currently unavailable.'
                        )

                        return redirect('create_order')

                    # Save the order item
                    order_item = item_form.save(commit=False)

                    # Store the menu item's name at order time
                    order_item.item_name = menu_item.name

                    # Store the selling price at order time
                    order_item.unit_price = menu_item.selling_price

                    # Connect the item to its order
                    order_item.order = order

                    # Save the order item
                    order_item.save()

                messages.success(
                    request,
                    'Order created successfully!'
                )

                return redirect('order_list')

            else:
                # Remove the incomplete order if its items are invalid
                order.delete()

        else:
            item_formset = OrderItemFormSet(request.POST)

    else:

        # Display empty forms for a new order
        order_form = OrderForm()

        item_formset = OrderItemFormSet()

    # Only show menu items that are available
    for form in item_formset:
        if 'menu_item' in form.fields:
            form.fields['menu_item'].queryset = MenuItem.objects.filter(
                is_available=True
            )

    context = {
        'order_form': order_form,
        'item_formset': item_formset,
    }

    return render(request, 'orders/create_order.html', context)


# =====================================================
# 3. VIEW ORDER DETAILS
# =====================================================

def order_detail(request, order_id):

    # Find the selected order
    order = get_object_or_404(Order, id=order_id)

    # Retrieve all items belonging to this order
    order_items = order.items.all()

    context = {
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'orders/order_detail.html', context)


# =====================================================
# 4. COMPLETE AN ORDER
# =====================================================

def complete_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':

        if order.status == 'ACTIVE':

            # Use the method already defined in our model
            order.complete_order()

            messages.success(
                request,
                'Order completed successfully!'
            )

        else:

            messages.error(
                request,
                'Only active orders can be completed.'
            )

    return redirect('order_list')


# =====================================================
# 5. CANCEL AN ORDER
# =====================================================

def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':

        if order.status == 'ACTIVE':

            # Use the cancellation method from our model
            order.cancel_order()

            messages.success(
                request,
                'Order cancelled successfully!'
            )

        else:

            messages.error(
                request,
                'Only active orders can be cancelled.'
            )

    return redirect('order_list')