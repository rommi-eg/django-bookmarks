from django.contrib.auth.models import User

from account.models import Profile


class EmailAuthBackend:
    """ Аутентификация посредством адреса электронной почты """
    def authenticate(self, request, username=None, password=None):
        """ Метод получает пользователя с данным адресом электронной почты"""
        try:
            user = User.objects.get(email=username)
            # Проверяем парольвстроенным методом check_password()
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
        
    def get_user(self, user_id):
        """ Метод получает пользователя по его id """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def create_profile(backend, user, *args, **kwargs):
    """ Создает профиль пользователя для социальной аутентификации """
    Profile.objects.get_or_create(user=user)
