from django.urls import path

# Import order views
from . import views


urlpatterns = [

    # Display all orders
    path('', views.order_list, name='order_list'),

    # Create a new order
    path('create/', views.create_order, name='create_order'),

    # View order details
    path('<int:order_id>/', views.order_detail, name='order_detail'),

    # Complete an order
    path(
        '<int:order_id>/complete/',
        views.complete_order,
        name='complete_order'
    ),

    # Cancel an order
    path(
        '<int:order_id>/cancel/',
        views.cancel_order,
        name='cancel_order'
    ),

]