from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.order_handler, name='order-list'),
    path('orders/', views.order_handler, name='create-order'),
    path('orders/<int:order_id>/', views.order_handler, name='order-handler'),
]
