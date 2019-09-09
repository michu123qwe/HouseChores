from . import views
from django.urls import path, include
from django.views.generic import TemplateView

app_name = 'accounts'
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.SignUp.as_view(), name='signup'),
]
