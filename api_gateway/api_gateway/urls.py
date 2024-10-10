from django.contrib import admin
from django.urls import path
from .views import ForwardView, LoginView, RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view(), name='user-login'),
    path('api/register/', RegisterView.as_view(), name='user-register'),
    path('api/<str:service>/', ForwardView.as_view()),
]
