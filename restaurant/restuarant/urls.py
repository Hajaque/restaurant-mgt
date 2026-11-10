# Import Django's path function
from django.urls import path

# Import our views
from . import views


urlpatterns = [

    # Main dashboard
    path('', views.dashboard, name='dashboard'),

    # Display all menu items
    path('menu/', views.menu_list, name='menu_list'),

    # Add a new menu item
    path('menu/add/', views.add_menu_item, name='add_menu_item'),

    # Edit an existing menu item using its ID
    path('menu/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),

    # Delete a menu item using its ID
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),

]