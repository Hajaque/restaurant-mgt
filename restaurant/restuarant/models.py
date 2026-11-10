# Import Decimal for accurate financial calculations.
# We use Decimal instead of float because floating-point numbers
# can produce rounding errors when calculating money.
from decimal import Decimal, ROUND_HALF_UP

# Import MinValueValidator to prevent users from entering
# invalid values, such as negative prices or zero quantities.
from django.core.validators import MinValueValidator

# Import Django's database models.
# This allows us to create database tables using Python classes.
from django.db import models

# Import timezone to record the exact time an order is completed.
from django.utils import timezone


# ============================================================
# 1. MENU ITEM MODEL
# ============================================================

# A Django model is a Python class that represents a database table.
#
# This class represents the restaurant's menu.
# It stores food, drinks and desserts.
class MenuItem(models.Model):

    # These are the categories available in our restaurant.
    #
    # The first value is stored in the database.
    # The second value is displayed to the user.
    CATEGORY_CHOICES = [
        ('FOOD', 'Food'),
        ('DRINK', 'Drink'),
        ('DESSERT', 'Dessert'),
    ]

    # Stores the name of the menu item.
    # For example: Chicken and Chips.
    #
    # CharField is used for short text.
    # max_length limits the name to 150 characters.
    name = models.CharField(max_length=150)

    # Stores a description of the menu item.
    # TextField allows longer text.
    # blank=True means the description is optional.
    description = models.TextField(blank=True)

    # Stores the category of the menu item.
    #
    # choices restrict the user to the categories
    # defined in CATEGORY_CHOICES.
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    # Stores the original price of the menu item.
    #
    # DecimalField is suitable for money because it
    # stores decimal values accurately.
    #
    # max_digits=10 means the number can contain
    # a maximum of 10 digits in total.
    #
    # decimal_places=2 allows two decimal places.
    #
    # MinValueValidator prevents negative prices.
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Determines whether the item is currently available.
    #
    # BooleanField stores either True or False.
    # The default value is True.
    is_available = models.BooleanField(default=True)

    # Automatically records the date and time
    # when the menu item is first created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Automatically updates the date and time
    # whenever the menu item is modified.
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------------------------------------------
    # SELLING PRICE PROPERTY
    # --------------------------------------------------------

    # @property allows us to access a method like an attribute.
    #
    # Instead of writing:
    # item.selling_price()
    #
    # We can write:
    # item.selling_price
    #
    # Our original OOP system adds a 5% service charge
    # to desserts.
    @property
    def selling_price(self):

        # Check whether the menu item belongs to the dessert category.
        if self.category == 'DESSERT':

            # Calculate the dessert price after adding 5%.
            #
            # 1.05 represents 100% of the original price
            # plus an additional 5%.
            #
            # quantize rounds the result to two decimal places.
            # ROUND_HALF_UP rounds a halfway value upward.
            return (self.price * Decimal('1.05')).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )

        # Food and drinks are sold at their original prices.
        return self.price

    # --------------------------------------------------------
    # STRING REPRESENTATION
    # --------------------------------------------------------

    # __str__ determines how an object is displayed as text.
    #
    # For example, instead of displaying:
    # MenuItem object (1)
    #
    # Django will display:
    # Chicken and Chips
    def __str__(self):
        return self.name

    # --------------------------------------------------------
    # MODEL CONFIGURATION
    # --------------------------------------------------------

    class Meta:

        # Display menu items alphabetically by category and name.
        ordering = ['category', 'name']

        # Names used by Django administration.
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'


# ============================================================
# 2. ORDER MODEL
# ============================================================

# The Order model represents a customer's order.
#
# One customer order can contain several menu items.
#
# For example:
# Order 1:
#   - Chicken and Chips
#   - Two Sodas
#   - One Ice Cream
class Order(models.Model):

    # Defines the possible statuses of an order.
    #
    # ACTIVE means the order is still being processed.
    # COMPLETED means the order has been finished.
    # CANCELLED means the order has been cancelled.
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # Stores the customer's name.
    #
    # The default value is Walk-in Customer.
    # This is useful when a customer does not provide a name.
    customer_name = models.CharField(
        max_length=150,
        default='Walk-in Customer'
    )

    # Stores the customer's table number.
    #
    # CharField allows us to use values such as:
    # 1, 2, 3, VIP-A or T-01.
    #
    # blank=True makes this field optional.
    table_number = models.CharField(
        max_length=20,
        blank=True
    )

    # Stores the current status of the order.
    #
    # The default status is ACTIVE whenever a new order
    # is created.
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    # Automatically records when the order is created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Automatically updates whenever the order is modified.
    updated_at = models.DateTimeField(auto_now=True)

    # Stores the date and time when the order is completed.
    #
    # null=True allows the database to store an empty value.
    # blank=True allows the field to be empty in forms.
    #
    # An order does not have a completion time until
    # someone completes it.
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # --------------------------------------------------------
    # CALCULATE ORDER SUBTOTAL
    # --------------------------------------------------------

    # @property allows us to access subtotal without
    # calling it as a normal method.
    #
    # Example:
    # order.subtotal
    #
    # This calculates the total cost of all items
    # belonging to the current order.
    @property
    def subtotal(self):

        # self.items.all() retrieves every OrderItem
        # connected to this particular order.
        #
        # line_total calculates quantity multiplied by
        # unit price for each order item.
        #
        # sum() adds all those line totals together.
        #
        # Decimal('0.00') provides the starting value
        # and ensures the result is a Decimal value.
        return sum(
            (item.line_total for item in self.items.all()),
            Decimal('0.00')
        )

    # --------------------------------------------------------
    # CALCULATE ORDER TOTAL
    # --------------------------------------------------------

    # At this stage, the total amount is equal to the subtotal.
    #
    # We separate this property because, in the future,
    # we may introduce discounts, taxes or delivery charges.
    @property
    def total_amount(self):
        return self.subtotal

    # --------------------------------------------------------
    # COMPLETE ORDER
    # --------------------------------------------------------

    # Changes the order status to COMPLETED.
    #
    # It also records the time the order was completed.
    def complete_order(self):

        # Update the order status.
        self.status = 'COMPLETED'

        # Record the current date and time.
        self.completed_at = timezone.now()

        # Save the changes to the database.
        self.save()

    # --------------------------------------------------------
    # CANCEL ORDER
    # --------------------------------------------------------

    # This method cancels an order.
    def cancel_order(self):

        # Change the current status to CANCELLED.
        self.status = 'CANCELLED'

        # Save the updated status in the database.
        self.save()

    # --------------------------------------------------------
    # STRING REPRESENTATION
    # --------------------------------------------------------

    # Displays the order using its ID and customer name.
    #
    # Example:
    # Order #1 - John
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    # --------------------------------------------------------
    # MODEL CONFIGURATION
    # --------------------------------------------------------

    class Meta:

        # Display the newest orders first.
        ordering = ['-created_at']


# ============================================================
# 3. ORDER ITEM MODEL
# ============================================================

# The OrderItem model represents an individual item
# inside a customer's order.
#
# For example:
#
# Order #1:
#   Chicken and Chips - Quantity 1
#   Soda              - Quantity 2
#   Ice Cream         - Quantity 1
#
# Each of these entries is stored as an OrderItem record.
class OrderItem(models.Model):

    # --------------------------------------------------------
    # RELATIONSHIP WITH ORDER
    # --------------------------------------------------------

    # ForeignKey creates a relationship between OrderItem and Order.
    #
    # Each OrderItem belongs to one Order.
    #
    # on_delete=models.CASCADE means:
    # If an order is deleted, its associated order items
    # will also be deleted.
    #
    # related_name='items' allows us to access an order's items
    # using:
    # order.items.all()
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # --------------------------------------------------------
    # RELATIONSHIP WITH MENU ITEM
    # --------------------------------------------------------

    # Connects an order item to an existing menu item.
    #
    # on_delete=models.PROTECT prevents a menu item from
    # being deleted while it is being referenced by an order.
    #
    # This helps preserve restaurant sales records.
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT
    )

    # --------------------------------------------------------
    # STORE ITEM DETAILS AT THE TIME OF ORDERING
    # --------------------------------------------------------

    # Stores a copy of the menu item's name.
    #
    # Why do we need this?
    #
    # Suppose a customer orders Chicken and Chips.
    # Later, the restaurant changes its name to Grilled Chicken.
    #
    # We still want the old order to display
    # Chicken and Chips.
    #
    # This field preserves the original name.
    item_name = models.CharField(max_length=150)

    # Stores the number of units ordered.
    #
    # PositiveIntegerField stores positive whole numbers.
    #
    # MinValueValidator ensures that the quantity is at least 1.
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    # Stores a copy of the item's selling price at the time
    # the customer places the order.
    #
    # This is important because menu prices may change later.
    #
    # The old customer's bill should retain the original price.
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # --------------------------------------------------------
    # CALCULATE ITEM TOTAL
    # --------------------------------------------------------

    # Calculates the total price of this particular order item.
    #
    # Formula:
    # Line Total = Quantity × Unit Price
    #
    # Example:
    # Soda quantity = 2
    # Unit price = UGX 3,000
    # Line total = UGX 6,000
    @property
    def line_total(self):

        # Multiply the quantity by the unit price.
        return self.quantity * self.unit_price

    # --------------------------------------------------------
    # STRING REPRESENTATION
    # --------------------------------------------------------

    # Displays the item name together with its quantity.
    #
    # Example:
    # Chicken and Chips x 2
    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    # --------------------------------------------------------
    # MODEL CONFIGURATION
    # --------------------------------------------------------

    class Meta:

        # Display order items according to their database IDs.
        ordering = ['id']

        # Prevents the same menu item from being stored
        # more than once in the same order.
        #
        # Instead, when a customer wants more of the same item,
        # we increase the quantity.
        #
        # The same menu item can still appear in different orders.
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'menu_item'],
                name='unique_menu_item_per_order'
            )
        ]