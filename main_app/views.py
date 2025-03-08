from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def welcome_page(request):
    context = {}
    return render(request, "welcome_page.html", context)


def auth_page(request):
    return render(request, "registrate.html")


def login_page(request):
    return render(request, "login.html")


@login_required
def logout_page(request):
    return redirect("")


def registration_page(request):
    return Ellipsis


@login_required
def profile_page(request):
    profile = request.user.profile
    return render(request,
                  "user_profile.hmtl",
                  {"profile": profile})


@login_required
def support_page(request):
    pass


@login_required
def filament_page(request):
    pass
