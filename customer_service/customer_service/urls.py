from django.urls import path
from . import views

urlpatterns = [
    path("", views.customer_view, name="customer-list-view"),
    path("customers/", views.customer_view, name="customer-list-create"),
    path("customers/<int:customerId>/", views.customer_view, name="customer-detail-update-delete"),
]
