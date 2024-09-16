from django.urls import path
from . import views

urlpatterns = [
    path('customers/list', views.list_customers, name='list-customers'),
    path('customers/', views.add_customer, name='add-customer'),
    path('customers/<int:customer_id>/', views.get_customer, name='get-customer'),
    path('customers/<int:customer_id>/update/', views.update_customer, name='update-customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete-customer'),
]
