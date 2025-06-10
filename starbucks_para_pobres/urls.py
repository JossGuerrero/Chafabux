"""
URL configuration for starbucks_para_pobres project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('cuentas/logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    # Cambiar contraseña
    path('cuentas/password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('cuentas/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    # path('cuentas/register/', views.register, name='register'),  # Descomenta si tienes vista de registro
    path('', include('startbucks.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)