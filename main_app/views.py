"""View-функции. Передают данные на html-страницы"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegistrationForm, LoginForm, ProfileEditForm, CheckoutForm
from .models import Profile, Printer, Cart, CartItem, CustomPrinter, Order, OrderItem


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
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
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

    if request.method == "POST" and "add_to_cart" in request.POST:
        return add_to_cart(request, printer)

    context = {
        "printer": printer,
    }
    return render(request, "printer_detail.html", context)


@login_required
def add_to_cart(request, printer):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        printer=printer,
        defaults={"quantity": 1, "user": request.user}  # Добавляем user при создании
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{printer.model} добавлен в корзину!")
    return redirect("printer_detail", pk=printer.id)


@login_required
def general_page(request):
    """Функция отображения страницы с каталогом принтеров"""
    printers = Printer.objects.all()
    context = {"pritners": printers}
    return render(request, "general.html", context)


def custom_printers_page(request):
    """View function for custom printers page"""
    return render(request,
                  "custom_printer_page.html",
                  {})


@login_required
def shopcart_page(request):
    """View-функция для страницы корзины"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        total_price = cart.total_price
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0

    context = {
        "cart_items": cart_items,
        "total_price": total_price
    }
    return render(request, "shopcart.html", context)


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "increase":
            item.quantity += 1
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1

        item.save()

    return redirect("shopcart")


@login_required
def remove_from_cart(request, item_id):
    """Функция удаления объекта из корзины"""
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Товар удален из корзины")
    return redirect("shopcart")


@login_required
def support_page(request):
    """View function for support page"""
    context = {}
    return render(request,
                  "support_page.html",
                  context)





@login_required
def checkout_page(request):
    # Получаем корзину текущего пользователя
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    # Если корзина пуста - редирект
    if not cart_items:
        messages.warning(request, "Ваша корзина пуста")
        return redirect("cart_view")

    total_price = cart.total_price

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
                total_price=total_price,
                payment_method=form.cleaned_data["payment_method"],
                notes=form.cleaned_data["notes"]
            )

            # Переносим товары из корзины в заказ
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    printer=cart_item.printer,
                    quantity=cart_item.quantity,
                    price=cart_item.printer.price
                )

            # Очищаем корзину
            cart_items.delete()

            messages.success(request, "Ваш заказ успешно оформлен! Номер заказа: #{}".format(order.id))
            return redirect("order_detail", order_id=order.id)
    else:
        # Заполняем форму данными из профиля пользователя
        initial_data = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        }

        try:
            profile = request.user.profile
            initial_data.update({
                "phone": profile.phone,
                "address": profile.billing_address,
            })
        except Profile.DoesNotExist:
            pass

        form = CheckoutForm(initial=initial_data)

    context = {
        "form": form,
        "cart_items": cart_items,
        "total_price": total_price,
    }

    return render(request, "checkout.html", context)