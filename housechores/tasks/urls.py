from django.urls import path
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:task_id>/complete_task/', views.complete_task, name='complete_task'),
    path('<int:task_id>/delete_task/', views.delete_task, name='delete_task'),
    path('create_task/', views.create_task, name='create_task'),
]
