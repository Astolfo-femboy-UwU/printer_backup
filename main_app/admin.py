from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Printer, CustomPrinter, Cart, CartItem, Order, OrderItem, ChatHistory


# Расширяем стандартный UserAdmin для отображения профиля
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ['card_number', 'expiry_month', 'expiry_year', 'card_holder_name',
              'billing_address', 'card_type']


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')


# Отменяем старую регистрацию User и регистрируем с кастомным админом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'card_type')
    list_filter = ('card_type',)
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'first_name', 'last_name', 'username', 'email')
        }),
        ('Платежная информация', {
            'fields': ('card_number', 'expiry_month', 'expiry_year',
                       'card_holder_name', 'billing_address', 'card_type')
        }),
    )


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ('model', 'article', 'price', 'dimensions', 'image_preview')
    list_filter = ('model',)
    search_fields = ('article', 'model', 'description')
    list_editable = ('price',)
    readonly_fields = ('image_preview',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('article', 'model', 'description', 'price')
        }),
        ('Характеристики', {
            'fields': ('dimensions', 'image_url')
        }),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return f'<img src="{obj.image_url}" width="50" height="50" />'
        return "Нет изображения"

    image_preview.allow_tags = True
    image_preview.short_description = "Изображение"


@admin.register(CustomPrinter)
class CustomPrinterAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'item_count', 'total_price')
    readonly_fields = ('created_at', 'total_price')

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = 'Количество товаров'

    def total_price(self, obj):
        return f"{obj.total_price} руб."

    total_price.short_description = 'Общая стоимость'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'printer', 'quantity', 'added_at', 'total_price')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'printer__model')

    def total_price(self, obj):
        return f"{obj.total_price} руб."

    total_price.short_description = 'Стоимость'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'first_name', 'last_name',
                    'total_price', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('order_number', 'user', 'status', 'total_price', 'payment_method')
        }),
        ('Информация о покупателе', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    actions = ['mark_as_completed', 'mark_as_shipped']

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} заказов помечено как завершенные")

    mark_as_completed.short_description = "Пометить как завершенные"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f"{queryset.count()} заказов помечено как отправленные")

    mark_as_shipped.short_description = "Пометить как отправленные"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'printer', 'quantity', 'price', 'total_price')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'printer__model')

    def total_price(self, obj):
        return f"{obj.total_price} руб."

    total_price.short_description = 'Общая стоимость'


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('truncated_user_message', 'truncated_bot_response', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_message', 'bot_response')
    readonly_fields = ('created_at',)

    def truncated_user_message(self, obj):
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message

    truncated_user_message.short_description = 'Сообщение пользователя'

    def truncated_bot_response(self, obj):
        return obj.bot_response[:50] + '...' if len(obj.bot_response) > 50 else obj.bot_response

    truncated_bot_response.short_description = 'Ответ бота'