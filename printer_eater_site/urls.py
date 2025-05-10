"""
URL configuration for printer_eater_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path("", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path("", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

from main_app.views import (welcome_page,
                            registration_page, login_page, logout_page,
                            profile_page, edit_profile_page,
                            custom_printers_page, general_page, printer_detail,
                            shopcart_page, checkout_page, update_cart_item, remove_from_cart,
                            support_page)


urlpatterns = [
    path("", welcome_page, name="welcome_page"),
    path("accounts/registration/", registration_page, name="registration_page"),
    path("accounts/login/", login_page, name="login_page"),
    path("accounts/logout/", logout_page, name="logout_page"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view()),
    path("profile/", profile_page, name="profile_page"),
    path("edit_profile/", edit_profile_page, name="edit_profile_page"),
    path("custom_printers/", custom_printers_page, name="custom_printers_page"),
    path("support/", support_page, name="support_page"),
    path("admin/", admin.site.urls),
    path("printer/<int:pk>/", printer_detail, name="printer_detail"),
    path("general/", general_page, name="general"),
    path("shopcart/", shopcart_page, name="shopcart"),
    path("checkout/", checkout_page, name="checkout"),
    path("shopcart/update/<int:item_id>/", update_cart_item, name="update_cart_item"),
    path("shopcart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
