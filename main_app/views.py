"""View-функции приложения main_app.

Содержит обработчики запросов для:
- Авторизации и регистрации пользователей
- Работы с профилем
- Взаимодействия с каталогом товаров
- Управления корзиной покупок
- Оформления заказов
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegistrationForm, LoginForm, ProfileEditForm, CheckoutForm
from .models import Profile, Printer, Cart, CartItem, Order, OrderItem


def welcome_page(request):
    """Обрабатывает запросы к главной странице.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse: Рендер шаблона welcome_page.html с контекстом:
            - printers (QuerySet): Список принтеров, отсортированный по цене
    """
    printers = Printer.objects.all().order_by("price")
    context = {"printers": printers}
    return render(request, "welcome_page.html", context)


def registration_page(request):
    """Обрабатывает регистрацию новых пользователей.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse:
            - При успешной регистрации: редирект на главную
            - При GET-запросе: рендер формы регистрации
    """
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
    """Обрабатывает аутентификацию пользователей.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse:
            - При успешном входе: редирект на главную
            - При ошибке: форма с сообщением об ошибке
    """
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
    """Обрабатывает выход пользователя из системы.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponseRedirect: Редирект на главную с сообщением об успешном выходе
    """
    logout(request)
    messages.success(request, "Вы успешно вышли из аккаунта")
    return redirect("/")


@login_required
def profile_page(request):
    """Отображает страницу профиля пользователя.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse: Рендер шаблона user_profile.html с контекстом:
            - profile (Profile): Профиль текущего пользователя
    """
    profile = request.user.profile
    return render(request,
                  "user_profile.html",
                  {"profile": profile})


@login_required
def edit_profile_page(request):
    """Обрабатывает редактирование профиля пользователя.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse:
            - При успешном сохранении: редирект на страницу профиля
            - При GET-запросе: форма редактирования профиля
    """
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
    """Отображает детальную страницу принтера.

    Args:
        request (HttpRequest): Объект запроса Django
        pk (int): ID принтера в базе данных

    Returns:
        HttpResponse: Рендер шаблона printer_detail.html с контекстом:
            - printer (Printer): Объект запрашиваемого принтера
    """
    printer = get_object_or_404(Printer, pk=pk)

    if request.method == "POST" and "add_to_cart" in request.POST:
        return add_to_cart(request, printer)

    context = {
        "printer": printer,
    }
    return render(request, "printer_detail.html", context)


@login_required
def add_to_cart(request, printer):
    """Добавляет принтер в корзину пользователя.

    Args:
        request (HttpRequest): Объект запроса Django
        printer (Printer): Объект добавляемого принтера

    Returns:
        HttpResponseRedirect: Редирект на страницу принтера с сообщением
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        printer=printer,
        defaults={"quantity": 1, "user": request.user}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{printer.model} добавлен в корзину!")
    return redirect("printer_detail", pk=printer.id)


@login_required
def general_page(request):
    """Отображает страницу каталога принтеров.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse: Рендер шаблона general.html с контекстом:
            - printers (QuerySet): Список всех принтеров
    """
    printers = Printer.objects.all()
    context = {"printers": printers}
    return render(request, "general.html", context)


def custom_printers_page(request):
    """Отображает страницу кастомных принтеров.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse: Рендер шаблона custom_printer_page.html
    """
    return render(request, "custom_printer_page.html", {})


@login_required
def shopcart_page(request):
    """Отображает страницу корзины пользователя.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse: Рендер шаблона shopcart.html с контекстом:
            - cart_items (QuerySet): Товары в корзине
            - total_price (Decimal): Общая стоимость заказа
    """
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
    """Обновляет количество товара в корзине.

    Args:
        request (HttpRequest): Объект запроса Django
        item_id (int): ID элемента корзины

    Returns:
        HttpResponseRedirect: Редирект на страницу корзины
    """
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        if request.method == "POST":
            action = request.POST.get("action")

            if action == "increase":
                item.quantity += 1
            elif action == "decrease":
                item.quantity = max(1, item.quantity - 1)

            item.save()
            messages.success(request, "Количество обновлено")
    except CartItem.DoesNotExist:
        messages.error(request, "Товар не найден в корзине")

    return redirect("shopcart")


@login_required
def remove_from_cart(request, item_id):
    """Удаляет товар из корзины.

    Args:
        request (HttpRequest): Объект запроса Django
        item_id (int): ID элемента корзины

    Returns:
        HttpResponseRedirect: Редирект на страницу корзины
    """
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.delete()
        messages.success(request, "Товар удален из корзины")
    except CartItem.DoesNotExist:
        messages.error(request, "Товар не найден в корзине")

    return redirect("shopcart")


@login_required
def support_page(request):
    """Отображает страницу поддержки.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse: Рендер шаблона support_page.html
    """
    context = {}
    return render(request, "support_page.html", context)


@login_required
def checkout_page(request):
    """Обрабатывает оформление заказа.

    Args:
        request (HttpRequest): Объект запроса Django

    Returns:
        HttpResponse:
            - При успешном оформлении: редирект на детали заказа
            - При GET-запросе: форма оформления заказа
    """
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Ваша корзина пуста")
        return redirect("shopcart")

    total_price = cart.total_price

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
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

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    printer=cart_item.printer,
                    quantity=cart_item.quantity,
                    price=cart_item.printer.price
                )

            cart_items.delete()
            messages.success(request, f"Ваш заказ успешно оформлен! Номер заказа: #{order.id}")
            return redirect("order_detail", order_id=order.id)
    else:
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
