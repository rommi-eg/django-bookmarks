from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """ Регистрация модели Profile в админке Django """
    list_display = (
        'user', 'date_of_birth', 'photo'
    )
    raw_id_fields = ('user', )
