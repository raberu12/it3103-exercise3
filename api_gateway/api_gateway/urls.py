from django.contrib import admin
from django.urls import path
from .views import LoginView, RegisterView, ProductView, OrderView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", LoginView.as_view(), name="user-login"),
    path("api/register/", RegisterView.as_view(), name="user-register"),
    path("api/products/", ProductView.as_view(), name="product"),
    path(
        "api/products/<int:productId>/",
        ProductView.as_view(),
        name="product-detail-update-delete",
    ),
    path("api/orders/", OrderView.as_view(), name="order-create"),
    path(
        "api/orders/<int:orderId>/",
        OrderView.as_view(),
        name="order-detail-update-delete",
    ),
]
