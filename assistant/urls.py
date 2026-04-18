from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/process-request/', views.process_request, name='process_request'),
    path('api/tasks/', views.get_tasks, name='get_tasks'),
    path('api/tasks/<str:task_code>/', views.get_task_detail, name='get_task_detail'),
    path('api/tasks/<str:task_code>/status/', views.update_status, name='update_status'),
]
