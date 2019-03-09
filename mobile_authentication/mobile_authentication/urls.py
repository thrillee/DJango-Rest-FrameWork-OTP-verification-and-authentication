
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/auth/', include('knox.urls')),
    path('rest-auth/', include('rest_auth.urls')),
]
