import redis

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from .forms import ImageCreateForm
from .models import Image
from actions.utils import create_action


r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                username=settings.REDIS_USER,
                password=settings.REDIS_PASSWORD)


@login_required
def image_create(request):
    """ Представление хранения изображений на сайте """
    if request.method == 'POST':
        # форма оиправлена
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # данные в форме валидны
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # назначаем текущего пользователя элементу
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request=request, message='Image added successfully')
            # перенаправляем к представлению детальной информации
            # о только чтосозданном элементе
            return redirect(new_image.get_absolute_url())
    else:
        # скомпановываем форму с данными, представленным букмарклетом
        # методом GET
        form = ImageCreateForm(data=request.GET)

    context = {'section': 'images', 'form': form}
    template = 'images/image/create.html'

    return render(request=request, template_name=template, context=context)


def image_deteil(request, id, slug):
    """ Представление для вывода изображения на страницу """
    image = get_object_or_404(Image, id=id, slug=slug)
    # увеличиваем общее число просмотров
    total_views = r.incr(f'image:{image.id}:views')
    # увеличиваем рейтинг изображения на 1
    r.zincrby('image_ranking', 1, image.id)
    context = {
        'section': 'images', 
        'image': image,
        'total_views': total_views
    }
    template = 'images/image/detail.html'
    return render(request=request, template_name=template, context=context)


@login_required # не дает пользователям, не вошедшим в систему, обращаться к этому представлению
@require_POST # разрешает запросы только методом POST
def image_like(request):
    """ Представление лайков и дизлайков """
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом,
        # то доставить первую страницу
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # Если AJAX-запрос и страница вне диапазона,
            # то вернуть пустую страницу
            return HttpResponse('')
        # Если страница вне диапазона, то вкреуть последнюю
        # страницу результатов
        images = paginator.page(paginator.num_pages)
    if images_only:
        context = {'section': 'images', 'images': images}
        template = 'images/image/list_images.html'
        return render(request=request, template_name=template, context=context)
    context = {'section': 'images', 'images': images}
    template = 'images/image/list.html'
    return render(request=request, template_name=template, context=context)


@login_required
def image_ranking(request):
    # получаем словарь рейтинга изображений
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(idx) for idx in image_ranking]
    # получаем наиболее просматриваемые изображения
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    context = {'section': 'image', 'most_viewed': most_viewed}
    template = 'images/image/rating.html'
    return render(request=request, template_name=template, context=context)
