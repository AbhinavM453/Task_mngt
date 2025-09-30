from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Taskapp.urls')),  # Include all your app URLs under /api/
]
