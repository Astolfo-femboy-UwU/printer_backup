"""Конфигурация форм"""
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Profile, Order


class RegistrationForm(forms.ModelForm):
    """Форма регистрации нового пользователя.

    Атрибуты:
        password (CharField): Поле для ввода пароля
        password2 (CharField): Поле для подтверждения пароля
    """
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    class Meta:
        """Мета-класс для настройки формы.

        Атрибуты:
            model (User): Модель, с которой связана форма
            fields (list): Список полей для отображения в форме
        """
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]

    def clean_first_name(self):
        """Валидация поля имени.

        Возвращает:
            str: Очищенное значение имени

        Raises:
            ValidationError: Если имя содержит не только буквы
        """
        first_name = self.cleaned_data.get("first_name")
        if not all(i.isalpha() for i in first_name):
            raise forms.ValidationError("Имя должно содержать только буквы")
        return first_name

    def clean_last_name(self):
        """Валидация поля фамилии.

        Возвращает:
            str: Очищенное значение фамилии

        Raises:
            ValidationError: Если фамилия содержит не только буквы
        """
        last_name = self.cleaned_data.get("last_name")
        if not all(i.isalpha() for i in last_name):
            raise forms.ValidationError("Фамилия должна содержать только буквы")
        return last_name

    def clean_username(self):
        """Проверка уникальности имени пользователя.

        Возвращает:
            str: Очищенное имя пользователя

        Raises:
            ValidationError: Если имя пользователя уже занято
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято")
        return username

    def clean_email(self):
        """Проверка уникальности email.

        Возвращает:
            str: Очищенный email

        Raises:
            ValidationError: Если email уже используется
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот адрес электронной почты уже используется")
        return email

    def clean_password2(self):
        """Проверка совпадения паролей.

        Возвращает:
            str: Подтвержденный пароль

        Raises:
            ValidationError: Если пароли не совпадают
        """
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2


class LoginForm(forms.Form):
    """Форма входа в систему.

    Атрибуты:
        username (CharField): Поле для ввода имени пользователя
        password (CharField): Поле для ввода пароля
    """
    username = forms.CharField(label="Имя пользователя", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        """Общая валидация формы входа.

        Вызывает:
            ValidationError: Если не введены имя пользователя или пароль
        """
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if not username or not password:
            raise forms.ValidationError("Пожалуйста, введите имя пользователя и пароль.")


class ProfileForm(forms.ModelForm):
    """Форма для создания профиля пользователя."""

    class Meta:
        """Мета-класс для настройки формы.

        Атрибуты:
            model (Profile): Модель профиля
            fields (list): Список полей для отображения
        """
        model = Profile
        fields = ["first_name", "last_name", "username", "email"]


class ProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля пользователя."""

    class Meta:
        """Мета-класс для настройки формы.

        Атрибуты:
            model (Profile): Модель профиля
            app_label (str): Название приложения
            fields (list): Список полей для редактирования
        """
        model = Profile
        app_label = "main_app"
        fields = [
            "first_name", "last_name", "email",
            "card_number", "expiry_month", "expiry_year",
            "card_holder_name", "billing_address", "card_type"
        ]

    def __init__(self, *args, **kwargs):
        """Инициализация формы с предзаполненными данными из модели User."""
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def clean_first_name(self):
        """Валидация поля имени."""
        first_name = self.cleaned_data.get("first_name")
        if not all(i.isalpha() for i in first_name):
            raise forms.ValidationError("Имя должно содержать только буквы")
        return first_name

    def clean_last_name(self):
        """Валидация поля фамилии."""
        last_name = self.cleaned_data.get("last_name")
        if not all(i.isalpha() for i in last_name):
            raise forms.ValidationError("Фамилия должна содержать только буквы")
        return last_name

    def clean_username(self):
        """Валидация имени пользователя."""
        username = self.cleaned_data.get("username")
        return username

    def clean_email(self):
        """Валидация email."""
        email = self.cleaned_data.get("email")
        return email

    # Поля для выбора срока действия карты
    expiry_month = forms.TypedChoiceField(
        choices=[(i, f"{i:02d}") for i in range(1, 13)],
        coerce=int,
        required=False,
        empty_value=None
    )
    expiry_year = forms.TypedChoiceField(
        choices=[(i, i) for i in range(timezone.now().year, timezone.now().year + 15)],
        coerce=int,
        required=False,
        empty_value=None
    )


class CheckoutForm(forms.Form):
    """Форма оформления заказа для интернет-магазина 3DPrintPro.

    Содержит все необходимые поля для сбора информации о покупателе,
    доставке и оплате заказа. Валидирует обязательные поля перед
    созданием заказа в системе.

    Attributes:
        first_name (CharField): Имя покупателя (обязательное поле).
        last_name (CharField): Фамилия покупателя (обязательное поле).
        email (EmailField): Электронная почта для уведомлений (обязательное).
        phone (CharField): Контактный телефон (обязательное поле).
        address (CharField): Адрес доставки с многострочным вводом.
        payment_method (ChoiceField): Способ оплаты (радио-кнопки).
        notes (CharField): Дополнительные пожелания к заказу (необязательное).
    """
    first_name = forms.CharField(
        label='Имя',
        max_length=100,
        required=True,
        help_text="Укажите ваше имя как в паспорте"
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=100,
        required=True,
        help_text="Укажите вашу фамилию"
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        help_text="На этот адрес придет подтверждение заказа"
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        required=True,
        help_text="Формат: +7XXXXXXXXXX"
    )
    address = forms.CharField(
        label='Адрес доставки',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Полный адрес с индексом и городом"
    )
    payment_method = forms.ChoiceField(
        label='Способ оплаты',
        choices=Order.PAYMENT_METHODS,
        widget=forms.RadioSelect,
        help_text="Выберите предпочтительный способ оплаты"
    )
    notes = forms.CharField(
        label='Примечания к заказу',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text="Дополнительные пожелания по доставке"
    )

    def clean_phone(self):
        """Валидация номера телефона.

        Проверяет корректность формата номера и нормализует его.

        Returns:
            str: Очищенный номер телефона.

        Raises:
            ValidationError: Если номер не соответствует ожидаемому формату.
        """
        phone = self.cleaned_data['phone']
        # Удаляем все нецифровые символы
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        if len(cleaned_phone) not in (10, 11):
            raise forms.ValidationError("Номер должен содержать 10-11 цифр")
        return f"+7{cleaned_phone[-10:]}"
