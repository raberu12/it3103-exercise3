from django.urls import path
from . import views

urlpatterns = [
    path("products/<int:productId>/", views.get_product, name="get-product"),  # New endpoint for getting a specific product
    path("products/all", views.product_list, name="product-list"),  # Endpoint for listing products
    path("products", views.create_product, name="create-product"),  # Endpoint for creating a new product
]
