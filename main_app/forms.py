from django import forms
from django.forms import CharField, EmailField
from django.contrib.auth.models import User
from .models import Profile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not all(i.isalpha for i in first_name):
            raise forms.ValidationError("Имя должно содержать только буквы")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not all(i.isalpha for i in last_name):
            raise forms.ValidationError("Фамилия должна содержать только буквы")
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято")
        return username

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


class LoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if not username or not password:
            raise forms.ValidationError("Пожалуйста, введите имя пользователя и пароль.")


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "username", "email"]


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        app_label = "main_app"
        fields = ["first_name", "last_name", "username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not all(i.isalpha for i in first_name):
            raise forms.ValidationError("Имя должно содержать только буквы")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not all(i.isalpha for i in last_name):
            raise forms.ValidationError("Фамилия должна содержать только буквы")
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get("username")
        # if User.objects.filter(username=username).exists():
        #     raise forms.ValidationError("Это имя пользователя уже занято")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # if User.objects.filter(email=email).exists():
        #     raise forms.ValidationError("Этот адрес электронной почты уже используется")
        return email
