from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.templatetags.static import static
from django.views.static import serve
import os
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('assetapp.urls')),
    path('login/',  auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('favicon.ico', RedirectView.as_view(url=static('images/favicon.png'), permanent=True)),
    path('sw.js', serve, {'document_root': settings.BASE_DIR / 'assetapp/static', 'path': 'sw.js'}),
    path('manifest.json', serve, {'document_root': settings.BASE_DIR / 'assetapp/static', 'path': 'manifest.json'}),
]