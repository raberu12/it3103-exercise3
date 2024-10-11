from django.contrib import admin
from django.urls import path
from .views import LoginView, RegisterView, ProductView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", LoginView.as_view(), name="user-login"),
    path("api/register/", RegisterView.as_view(), name="user-register"),
    path("api/products/", ProductView.as_view(), name="product-create"),
    path(
        "api/products/<int:productId>/",
        ProductView.as_view(),
        name="product-detail-update-delete",
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
