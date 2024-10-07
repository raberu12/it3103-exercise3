from django.contrib import admin
from django.urls import path
from .views import ForwardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/<str:service>/', ForwardView.as_view()),
]
