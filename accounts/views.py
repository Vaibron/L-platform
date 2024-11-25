from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from .forms import LoginForm
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  # Используем стандартную форму
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Попытка аутентификации
            user = authenticate(username=username, password=password)
            if user is not None:
                # Если аутентификация прошла успешно, логиним пользователя
                login(request, user)
                return redirect('profile')  # Перенаправление на ЛК (например, профиль)
            else:
                # Если аутентификация не удалась
                form.add_error(None, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем пользователя с хешированным паролем
            return redirect('login')  # Перенаправляем на страницу входа
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
