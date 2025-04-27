from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Модель профиля пользователя, расширяющая стандартную модель User.

    Содержит дополнительную информацию о пользователе, включая платежные данные.

    Attributes:
        user (OneToOneField): Связь один-к-одному с моделью User
        first_name (TextField): Имя пользователя
        last_name (TextField): Фамилия пользователя
        username (TextField): Имя пользователя (дублирует User.username)
        email (EmailField): Электронная почта (дублирует User.email)
        card_number (CharField): Номер кредитной карты
        expiry_month (PositiveIntegerField): Месяц окончания действия карты
        expiry_year (PositiveIntegerField): Год окончания действия карты
        card_holder_name (CharField): Имя владельца карты
        billing_address (TextField): Адрес для выставления счета
        card_type (CharField): Тип кредитной карты (Visa, MasterCard и т.д.)
    """

    class Meta:
        """Мета-класс для определения метаданных модели.

        Attributes:
            app_label (str): Указывает приложение, к которому принадлежит модель
        """
        app_label = "main_app"

    CARD_TYPE_CHOICES = [
        ("visa", "Visa"),
        ("mastercard", "MasterCard"),
        ("amex", "American Express"),
        ("discover", "Discover"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(max_length=100, blank=True)
    last_name = models.TextField(max_length=100, blank=True)
    username = models.TextField(max_length=25, blank=True)
    email = models.EmailField(null=True, blank=True)

    # Платёжные данные
    card_number = models.CharField(max_length=19, blank=True)
    expiry_month = models.PositiveIntegerField(null=True, blank=True)
    expiry_year = models.PositiveIntegerField(null=True, blank=True)
    card_holder_name = models.CharField(max_length=100, blank=True)
    billing_address = models.TextField(blank=True)
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        blank=True
    )


class Printer(models.Model):
    """Модель для представления 3D-принтеров в системе.

    Attributes:
        description (TextField): Подробное описание принтера
        article (CharField): Уникальный артикул принтера
        price (DecimalField): Цена принтера
        dimensions (CharField): Габаритные размеры (ШxГxВ)
        model (CharField): Модель принтера
    """

    class Meta:
        """Мета-класс для определения метаданных модели.

        Attributes:
            app_label (str): Указывает приложение, к которому принадлежит модель
        """
        app_label = "main_app"

    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    article = models.CharField(verbose_name="Артикул", blank=True, max_length=100, unique=True)
    price = models.DecimalField(verbose_name="Цена", blank=True, default=0, max_digits=10, decimal_places=2)
    dimensions = models.CharField(verbose_name="Габариты", blank=True, max_length=50, help_text="Формат: ШхГхВ (мм)")
    model = models.CharField(verbose_name="Модель", blank=True, max_length=100)

    def __str__(self):
        """Строковое представление объекта Printer.

        Returns:
            str: Строка в формате "Производитель Артикул"
        """
        return f"{self.model} {self.article}"


class CustomPrinter(models.Model):
    """Модель для кастомных (настроенных) 3D-принтеров.

    Пока не реализована полностью, служит для будущего расширения функционала.
    """

    class Meta:
        """Мета-класс для определения метаданных модели.

        Attributes:
            app_label (str): Указывает приложение, к которому принадлежит модель
        """
        app_label = "main_app"


class Cart(models.Model):
    """Модель корзины покупок пользователя.

    Attributes:
        user (OneToOneField): Связь с пользователем (один пользователь - одна корзина)
        created_at (DateTimeField): Дата и время создания корзины
        updated_at (DateTimeField): Дата и время последнего обновления корзины
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Строковое представление объекта Cart.

        Returns:
            str: Строка в формате "Корзина пользователя username"
        """
        return f"Корзина пользователя {self.user.username}"

    @property
    def total_price(self):
        """Вычисляет общую стоимость всех товаров в корзине.

        Returns:
            Decimal: Суммарная стоимость всех товаров в корзине
        """
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Модель элемента корзины покупок.

    Attributes:
        user (ForeignKey): Связь с пользователем (для быстрого доступа)
        cart (ForeignKey): Связь с корзиной
        printer (ForeignKey): Связь с принтером
        quantity (PositiveIntegerField): Количество единиц товара
        added_at (DateTimeField): Дата и время добавления товара в корзину
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Мета-класс для определения метаданных модели.

        Attributes:
            unique_together (tuple): Гарантирует уникальность пары (корзина, принтер)
        """
        unique_together = ('cart', 'printer')  # Один принтер - одна позиция в корзине

    def __str__(self):
        """Строковое представление объекта CartItem.

        Returns:
            str: Строка в формате "Количество x Модель Артикул"
        """
        return f"{self.quantity} x {self.printer.model} {self.printer.article}"

    @property
    def total_price(self):
        """Вычисляет общую стоимость позиции (цена * количество).

        Returns:
            Decimal: Стоимость позиции (цена принтера * количество)
        """
        return self.printer.price * self.quantity

