from django.urls import path
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:task_id>/complete_task/', views.complete_task, name='complete_task'),
]