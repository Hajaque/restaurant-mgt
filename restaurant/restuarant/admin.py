# Import Django administration tools.
from django.contrib import admin

# Import our three database models.
from .models import MenuItem, Order, OrderItem


# ============================================================
# 1. ORDER ITEM INLINE
# ============================================================

# Allows us to add and manage order items directly
# inside the administration page of an order.
class OrderItemInline(admin.TabularInline):

    # The model that this inline manages.
    model = OrderItem

    # Display one empty row when adding a new order.
    extra = 1

    # Fields displayed in the order items table.
    fields = (
        'menu_item',
        'quantity',
        'item_name',
        'unit_price',
        'line_total',
    )

    # These fields are calculated or copied automatically.
    readonly_fields = (
        'item_name',
        'unit_price',
        'line_total',
    )

    # Automatically copy the menu item details
    # when an order item is saved.
    def save_formset(self, request, form, formset, change):

        # Get the order items that have been submitted.
        instances = formset.save(commit=False)

        # Delete order items that the administrator removed.
        for obj in formset.deleted_objects:
            obj.delete()

        # Save each order item.
        for instance in instances:

            # Only copy the details when creating a new item.
            if not instance.pk:
                instance.item_name = instance.menu_item.name

                # Use selling_price to include the dessert
                # service charge where applicable.
                instance.unit_price = instance.menu_item.selling_price

            instance.save()

        # Save any many-to-many relationships.
        formset.save_m2m()


# ============================================================
# 2. MENU ITEM ADMIN
# ============================================================

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    # Columns displayed in the menu items list.
    list_display = (
        'name',
        'category',
        'price',
        'selling_price_display',
        'is_available',
        'created_at',
    )

    # Allow filtering by category and availability.
    list_filter = (
        'category',
        'is_available',
    )

    # Add a search box for menu items.
    search_fields = (
        'name',
        'description',
    )

    # Allow availability to be changed directly in the list.
    list_editable = (
        'is_available',
    )

    # Display newest menu items first.
    ordering = ('-created_at',)

    # Display 20 records per page.
    list_per_page = 20

    # Prevent manual editing of automatically generated dates.
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Display the calculated selling price.
    @admin.display(description='Selling Price (UGX)')
    def selling_price_display(self, obj):
        return obj.selling_price


# ============================================================
# 3. ORDER ADMIN
# ============================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # Columns displayed in the orders list.
    list_display = (
        'id',
        'customer_name',
        'table_number',
        'status',
        'created_at',
        'total_display',
    )

    # Allow filtering by order status and creation date.
    list_filter = (
        'status',
        'created_at',
    )

    # Allow searching for orders using customer details.
    search_fields = (
        'customer_name',
        'table_number',
    )

    # Display newest orders first.
    ordering = ('-created_at',)

    # Display 20 orders per page.
    list_per_page = 20

    # Allow order items to be managed inside an order.
    inlines = [OrderItemInline]

    # Automatically calculated fields cannot be edited.
    readonly_fields = (
        'created_at',
        'updated_at',
        'completed_at',
        'subtotal_display',
        'total_display',
    )

    # Organise the fields displayed when opening an order.
    fields = (
        'customer_name',
        'table_number',
        'status',
        'created_at',
        'updated_at',
        'completed_at',
        'subtotal_display',
        'total_display',
    )

    # Calculate and display the order subtotal.
    @admin.display(description='Subtotal (UGX)')
    def subtotal_display(self, obj):
        return obj.subtotal

    # Display the final order amount.
    @admin.display(description='Total Amount (UGX)')
    def total_display(self, obj):
        return obj.total_amount

    # --------------------------------------------------------
    # ADMIN ACTION: COMPLETE ORDERS
    # --------------------------------------------------------

    # Allows the administrator to complete multiple orders.
    @admin.action(description='Mark selected orders as completed')
    def mark_as_completed(self, request, queryset):

        # Select only orders that are currently active.
        active_orders = queryset.filter(status='ACTIVE')

        # Count the number of orders being completed.
        count = active_orders.count()

        # Complete each selected order.
        for order in active_orders:
            order.complete_order()

        # Display a confirmation message.
        self.message_user(
            request,
            f'{count} order(s) successfully completed.'
        )

    # --------------------------------------------------------
    # ADMIN ACTION: CANCEL ORDERS
    # --------------------------------------------------------

    # Allows the administrator to cancel multiple orders.
    @admin.action(description='Cancel selected orders')
    def cancel_orders(self, request, queryset):

        # Only cancel active orders.
        active_orders = queryset.filter(status='ACTIVE')

        count = active_orders.count()

        for order in active_orders:
            order.cancel_order()

        self.message_user(
            request,
            f'{count} order(s) successfully cancelled.'
        )

    # Register our custom actions.
    actions = [
        'mark_as_completed',
        'cancel_orders',
    ]


# ============================================================
# 4. ORDER ITEM ADMIN
# ============================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    # Display order item information in a table.
    list_display = (
        'order',
        'item_name',
        'quantity',
        'unit_price',
        'line_total',
    )

    # Allow searching by item name or customer name.
    search_fields = (
        'item_name',
        'order__customer_name',
    )

    # Allow filtering by order status.
    list_filter = (
        'order__status',
    )

    # Display newest order items first.
    ordering = ('-id',)