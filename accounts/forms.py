from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', max_length=255)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Поле для пароля

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # Включите нужные поля

    def save(self, commit=True):
        user = super().save(commit=False)  # Создание пользователя, но без сохранения
        user.set_password(self.cleaned_data["password"])  # Хешируем пароль
        if commit:
            user.save()  # Сохраняем пользователя в БД
        return user
