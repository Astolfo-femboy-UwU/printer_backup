from django import forms
from django.forms import CharField, EmailField
from django.contrib.auth.models import User
from .models import Profile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "nickname", "email", "password"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not all(i.isalpha for i in name):
            raise forms.ValidationError("Имя должно содержать только буквы")
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get("name")
        if not all(i.isalpha for i in surname):
            raise forms.ValidationError("Фамилия должна содержать только буквы")
        return surname

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if User.objects.filter(username=nickname).exists():
            raise forms.ValidationError("Это имя пользователя уже занято")
        return nickname

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот адрес электронной почты уже используется")
        return email

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2


class LoginForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Имя',
            'class': 'form-control'
        }),
        label="Имя пользователя"
    )
    surname = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Фамилия',
            'class': 'form-control'
        }),
    )
    nickname = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Никнейм',
            'class': 'form-control'
        }),
        label='Никнейм'
    )
    email = forms.EmailField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Адрес электронной почты',
            'class': 'form-control'
        }),
        label='Адрес электронной почты'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
            'class': 'form-control'
        }),
        label='Пароль'
    )
