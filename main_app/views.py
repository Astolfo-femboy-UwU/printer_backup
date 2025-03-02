from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def welcome_page(request):
    pass


def login_page(request):
    return Ellipsis


@login_required
def logout_page(request):
    return Ellipsis


def registration_page(request):
    return Ellipsis


@login_required
def support_page(request):
    pass


@login_required
def filament_page(request):
    pass
