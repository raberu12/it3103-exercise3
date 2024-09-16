from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.product_view, name="product-list-create"),
    path("products/<int:productId>/", views.product_view, name="product-detail-update-delete"),
]
