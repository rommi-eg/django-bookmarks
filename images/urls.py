from django.urls import path

from . import views


app_name = 'images'

urlpatterns = [
    path('create/', view=views.image_create, name='create'),
    path('detail/<int:id>/<slug:slug>/', view=views.image_deteil, name='detail'),
    path('like/', view=views.image_like, name='like'),
    path('', view=views.image_list, name='list'),
    path('ranking/', view=views.image_ranking, name='ranking'),
]

