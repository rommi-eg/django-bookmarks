from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from actions.utils import create_action
from actions.models import Action


'''
# Вариант представления входа пользователя в систему
def user_login(request):
    """ Представление входа в систему """
    # Если метод запроса POST
    if request.method == 'POST':
        # Создаем экземпляр новой формы с переданными данными
        form = LoginForm(request.POST)
        # Валидируем форму и если она волидна
        if form.is_valid():
            # Получаем данные из формы в виде словаря
            cd = form.cleaned_data
            # Аутентифицируем пользователя по базе данных методом authenticate(), 
            # который принимает объект request парвметры username и password и
            # возвращает объект User, если пользователь был успешно аутетифицирован 
            # или None в противном случае  
            user = authenticate(
                request=request,
                username=cd['username'],
                password=cd['password'],
            )
            # Если пользователь успешно аутентифицирован
            if user is not None:
                # Проверяем статус, путем обращения к атрибуту is_active модели User
                if user.is_active:
                    # Если пользователь активен, то задаем пользователя в текущем 
                    # сеансе путем вызова метода login()
                    login(request=request, user=user)
                    return HttpResponse('Authenticated successfully')
                else:
                    # Если пользователь не активен
                    return HttpResponse('Disabled account')
            else:
                # Если пользователь небыл успещно аутентифицирован
                return HttpResponse('Invalid login')
    else:
        # Создаем экземпляр новой формы, если метод запроса GET
        form = LoginForm()

    context = {'form': form}
    template = 'account/login.html'

    return render(request=request, template_name=template, context=context)


@login_required
def user_logout(request):
    """ Представление выхода пользователя из системы """
    logout(request)
    context = {}
    template = 'registration/logged_out.html'
    return render(request=request, template_name=template, context=context)
'''


# Декоратор проверяет аутентификацию текущего пользователя
# Если пользователь аутентифицирован, то исполняется декорированное 
# предстасвление; если нет, то перенаправляет пользователя на 
# изначально запрошенный url. С этой целью добавлен скрытый
# элемент input с именем next
@login_required
def dashboard(request):
    """ Представление Dashboard """
    # По-умолчанию, показать все действия
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # Если пользователь подписан на других,
        # то извлечь только их действия
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile')[:10].prefetch_related('target')[:10]
    context = {'section': 'dashboard', 'actions': actions}
    template = 'account/dashboard.html'
    return render(request=request, template_name=template, context=context)


def register(request):
    """ Представление регистрации пользователя """
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Создаем новый объект пользователя, но пока не сохраняем его
            new_user = user_form.save(commit=False)
            # Устанавливаем выбранный пароль. Данный метод хеширует пароль
            # перед его сохранением в базе данных.
            new_user.set_password(user_form.cleaned_data['password'])
            # Сохраняем объект User
            new_user.save()
            # Создаем профиль пользователя
            Profile.objects.create(user=new_user)
            create_action(request.user, 'has created an account')

            context = {'new_user': new_user}
            template = 'account/register_done.html'

            return render(request=request, template_name=template, context=context)
    else:
        user_form = UserRegistrationForm()

    context = {'user_form': user_form}
    template = 'account/register.html'

    return render(request=request, template_name=template, context=context)


@login_required
def edit(request):
    """ Представление редактирования личной информации пользователя """
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request=request, message='Profile update successfully')
        else:
            messages.error(request=request, message='Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {'user_form': user_form, 'profile_form': profile_form}
    template = 'account/edit.html'

    return render(request=request, template_name=template, context=context)


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    context = {'section': 'people', 'users': users}
    template = 'account/user/list.html'
    return render(request=request, template_name=template, context=context)


@login_required
def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    context = {'section': 'people', 'user': user}
    template = 'account/user/detail.html'
    return render(request=request, template_name=template, context=context)


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user,
                                              user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
