from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User task APIs
    path('tasks/', views.user_tasks, name='user_tasks'),
    path('tasks/<int:pk>/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:pk>/report/', views.task_report, name='task_report'),

    # Admin panel APIs
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:pk>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/assign/', views.assign_user_to_admin, name='assign_user_to_admin'),

    path('admin/tasks/', views.admin_tasks, name='admin_tasks'),
    path('admin/tasks/<int:pk>/', views.admin_task_update, name='admin_task_update'),
]
