from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegistrationForm, LoginForm, ProfileEditForm
from .models import Profile, Printer


def welcome_page(request):
    """View function for the main (welcome) page"""
    printers = Printer.objects.all().order_by("price")
    context = {"printers": printers}
    return render(request, "welcome_page.html", context)


def registration_page(request):
    """View function for registration"""
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


def login_page(request):
    """View function for logging in"""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            form.add_error(None, "Неверное имя пользователя или пароль.")
    else:
        form = LoginForm()
    return render(request,
                  "registration/login.html",
                  {"form": form})


@login_required
def logout_page(request):
    """View function for logging out"""
    logout(request)
    messages.success(request, "Вы успешно вышли из аккаунта")
    return redirect("/")


@login_required
def profile_page(request):
    """View function for profile page"""
    profile = request.user.profile
    return render(request,
                  "user_profile.html",
                  {"profile": profile})


@login_required
def edit_profile_page(request):
    """View function for editing profile page"""
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
        messages.error(request, "Ошибки в форме")
    else:
        form = ProfileEditForm(instance=profile)
    return render(request,
                  "edit_profile.html",
                  {"form": form})


def printer_detail(request, pk):
    printer = get_object_or_404(Printer, pk=pk)
    print(f"Found printer: {printer}")
    context = {
        'printer': printer,
        'printers': Printer.objects.exclude(pk=pk)[:4]
    }
    return render(request, 'printer_detail.html', context)


def custom_printers_page(request):
    """View function for custom printers page"""
    return render(request,
                  "custom_printer_page.html",
                  {})


@login_required
def support_page(request):
    """View function for support page"""
    context = {}
    return render(request,
                  "support_page.html",
                  context)


def test_view(request, pk):
    printer = get_object_or_404(Printer, pk=pk)
    return render(request, 'test.html', {'printer': printer})
