from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from .models import *
from django.views.decorators.cache import never_cache


def welcome_page(request):
    return render(request, "welcome_page.html", {})


def registration_page(request):
    if request.method == "POST":
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            user = User(
                first_name=reg_form.cleaned_data["first_name"],
                last_name=reg_form.cleaned_data["last_name"],
                username=reg_form.cleaned_data["username"],
                email=reg_form.cleaned_data["email"]
            )
            user.set_password(reg_form.cleaned_data["password"])
            user.save()
            login(request, user)
            Profile.objects.create(user=user)
            return redirect("/")
    else:
        reg_form = RegistrationForm()

    return render(request,
                  "registration/registration_page.html",
                  {"reg_form": reg_form})


@never_cache
def login_page(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                form.add_error(None, "Неверное имя пользователя или пароль.")
        else:
            Ellipsis
    else:
        form = LoginForm()
    return render(request,
                  "registration/login.html",
                  {"form": form})


@login_required
def logout_page(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из аккаунта")
    return redirect("/")


@login_required
def profile_page(request):
    profile = request.user.profile
    return render(request,
                  "user_profile.html",
                  {"profile": profile})


@login_required
def edit_profile_page(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            profile.save()
            messages.success(request, "Профиль успешно обновлён")
            return redirect("/profile/")
        else:
            messages.error(request, "Ошибки в форме")
    else:
        form = ProfileEditForm(instance=profile)
    return render(request,
                  "edit_profile.html",
                  {"form": form})


def printers_page(request):
    return render(request,
                  "printers_page.html",
                  {})


def custom_printers_page(request):
    return render(request,
                  "custom_printer_page.html",
                  {})


@login_required
def support_page(request):
    context = {}
    return render(request,
                  "support_page.html",
                  {})

