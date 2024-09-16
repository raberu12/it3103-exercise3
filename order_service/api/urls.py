from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.create_order, name='create-order'),
    path('orders/list/', views.get_order_list, name='order-list'),
    path('orders/<int:order_id>/', views.get_order, name='get-order'),
    path('orders/<int:order_id>/update/', views.update_order, name='update-order'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete-order'),
]
