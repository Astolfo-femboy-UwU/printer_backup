from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegistrationForm, LoginForm, ProfileEditForm
from .models import Profile, Printer, Cart, CartItem, CustomPrinter


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


@login_required
def printer_detail(request, pk):
    printer = get_object_or_404(Printer, pk=pk)
    context = {
        'printer': printer,
    }
    return render(request, 'printer_detail.html', context)


@login_required
def general_page(request):
    printers = Printer.objects.all()
    return render(request, "general.html")


def custom_printers_page(request):
    """View function for custom printers page"""
    return render(request,
                  "custom_printer_page.html",
                  {})


def shopcart_page(request):
    """123"""
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'shopcart.html', context)


@login_required
def support_page(request):
    """View function for support page"""
    context = {}
    return render(request,
                  "support_page.html",
                  context)


def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increment':
            item.quantity += 1
        elif action == 'decrement' and item.quantity > 1:
            item.quantity -= 1
        item.save()
    return redirect('shopcart')


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('shopcart')
