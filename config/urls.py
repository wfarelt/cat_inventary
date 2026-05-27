from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('authentication.urls')),
    path('users/', include('users.urls')),
    path('company/', include('company.urls')),
    path('settings/', include('settings_app.urls')),
]
