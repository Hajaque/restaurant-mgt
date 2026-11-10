from decimal import Decimal

# Import Django functions
from django.shortcuts import render, redirect, get_object_or_404

# Import messages to display success and error notifications
from django.contrib import messages

# Q allows us to search multiple fields at the same time
from django.db.models import Q

# Import our models
from .models import MenuItem, Order

# Import our menu form
from .forms import MenuItemForm


# ==========================================================
# 1. DASHBOARD VIEW
# ==========================================================

def dashboard(request):

    # Count all menu items
    total_menu_items = MenuItem.objects.count()

    # Count menu items that are available
    available_menu_items = MenuItem.objects.filter(
        is_available=True
    ).count()

    # Count all orders
    total_orders = Order.objects.count()

    # Count active orders
    active_orders = Order.objects.filter(
        status='ACTIVE'
    ).count()

    # Count completed orders
    completed_orders = Order.objects.filter(
        status='COMPLETED'
    ).count()

    # Count cancelled orders
    cancelled_orders = Order.objects.filter(
        status='CANCELLED'
    ).count()

    # Calculate revenue from completed orders only.
    completed_order_items = Order.objects.filter(status='COMPLETED')
    total_revenue = sum(
        (order.total_amount for order in completed_order_items),
        Decimal('0.00')
    )

    # Retrieve the five most recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]

    # Send the information to the dashboard template
    context = {
        'total_menu_items': total_menu_items,
        'available_menu_items': available_menu_items,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    }

    return render(request, 'restaurant/dashboard.html', context)


# ==========================================================
# 2. VIEW ALL MENU ITEMS
# ==========================================================

def menu_list(request):

    # Retrieve all menu items from the database
    menu_items = MenuItem.objects.all()

    # Get the search text entered by the user
    search_query = request.GET.get('search', '')

    # Get the selected category
    selected_category = request.GET.get('category', '')

    # Get the selected availability
    selected_availability = request.GET.get('availability', '')

    # SEARCH FUNCTIONALITY
    if search_query:

        # Search both the name and description fields
        menu_items = menu_items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # CATEGORY FILTER
    if selected_category:

        menu_items = menu_items.filter(
            category=selected_category
        )

    # AVAILABILITY FILTER
    if selected_availability == 'available':

        menu_items = menu_items.filter(
            is_available=True
        )

    elif selected_availability == 'unavailable':

        menu_items = menu_items.filter(
            is_available=False
        )

    # Arrange menu items alphabetically
    menu_items = menu_items.order_by('name')

    # Send information to the HTML template
    # Prepare information to send to the HTML template
 # Prepare information to send to the HTML template
    context = {
    'menu_items': menu_items,
    'search_query': search_query,
    'selected_category': selected_category,
    'selected_availability': selected_availability,

    # Get categories directly from our MenuItem model
    'categories': MenuItem.CATEGORY_CHOICES,
}

    return render(request, 'restaurant/menu_list.html', context)


# ==========================================================
# 3. ADD A NEW MENU ITEM
# ==========================================================

def add_menu_item(request):

    # Check whether the user has submitted the form
    if request.method == 'POST':

        # Collect the submitted information
        form = MenuItemForm(request.POST)

        # Check whether the information is valid
        if form.is_valid():

            # Save the new menu item to the database
            form.save()

            # Display a success message
            messages.success(request, 'Menu item added successfully!')

            # Return to the menu list
            return redirect('menu_list')

    else:

        # Display an empty form when the page is first opened
        form = MenuItemForm()

    return render(
        request,
        'restaurant/menu_form.html',
        {
            'form': form,
            'page_title': 'Add Menu Item',
            'button_text': 'Save Menu Item'
        }
    )


# ==========================================================
# 4. EDIT AN EXISTING MENU ITEM
# ==========================================================

def edit_menu_item(request, item_id):

    # Find the menu item using its ID.
    # If it does not exist, Django returns a 404 error.
    menu_item = get_object_or_404(MenuItem, id=item_id)

    if request.method == 'POST':

        # Load the existing item into the form and update it
        form = MenuItemForm(request.POST, instance=menu_item)

        if form.is_valid():

            # Save the updated information
            form.save()

            messages.success(request, 'Menu item updated successfully!')

            return redirect('menu_list')

    else:

        # Display the existing information in the form
        form = MenuItemForm(instance=menu_item)

    return render(
        request,
        'restaurant/menu_form.html',
        {
            'form': form,
            'page_title': 'Edit Menu Item',
            'button_text': 'Update Menu Item'
        }
    )


# ==========================================================
# 5. DELETE A MENU ITEM
# ==========================================================

def delete_menu_item(request, item_id):

    # Find the menu item that should be deleted
    menu_item = get_object_or_404(MenuItem, id=item_id)

    if request.method == 'POST':

        # Delete the selected menu item
        menu_item.delete()

        messages.success(request, 'Menu item deleted successfully!')

        return redirect('menu_list')

    # Display a confirmation page before deleting
    return render(
        request,
        'restaurant/menu_confirm_delete.html',
        {
            'menu_item': menu_item
        }
    )