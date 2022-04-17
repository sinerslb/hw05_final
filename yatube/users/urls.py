# users/urls.py

# Импортируем из приложения django.contrib.auth нужный view-класс
from django.contrib.auth.views import (LoginView,
                                       LogoutView,
                                       PasswordResetView,
                                       PasswordChangeView,
                                       PasswordChangeDoneView,
                                       PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)

from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    # регистрация
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),

    # выход
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),

    # вход
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),

    # смена пароля подтверждение
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),

    # смена пароля
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change'
    ),

    # Восстановление пароля
    path(
        'password_reset/', PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset'
    ),

    # Сообщение об отправке ссылки для восстановления пароля
    path(
        'password_reset/done/', PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # Вход по ссылке для восстановления пароля
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    # Сообщение об успешном восстановлении пароля
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
