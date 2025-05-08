from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

"""
urlpatterns = [
    # предыдущие url входа и выхода
    # path('login/', view=views.user_login, name='login'),
    # path('logout/', view=views.user_logout, name='logout'),

    # url-адреса входа и выхода
    path('login/', view=auth_views.LoginView.as_view(), name='login'),
    path('logout/', view=auth_views.LogoutView.as_view(), name='logout'),

    # url-адреса смены пароля
    path('password-change/', view=auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('passwoed-change/done/', view=auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # url-адреса сброса пароля
    path('password-reset/', view=auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', view=auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', view=auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', view=auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # url-адрес dashboard
    path('', view=views.dashboard, name='dashboard'),
]
"""

urlpatterns = [
    # дабавлены все необходимые представления аутентификации, что написаны выше
    path('', include('django.contrib.auth.urls')),

    # url-адрес dashboard
    path('', view=views.dashboard, name='dashboard'),

    # url-адрес регистрации пользователя
    path('register/', view=views.register, name='register'),

    # url-адрес редактирования профиля пользователя
    path('edit/', view=views.edit, name='edit'),

    path('users/', view=views.user_list, name='user_list'),
    path('users/follow/', view=views.user_follow, name='user_follow'),
    path('users/<username>/', view=views.user_detail, name='user_detail'),
]
