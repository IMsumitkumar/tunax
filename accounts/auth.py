from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import DiscordUser


class DiscordAuthenticationBackend(ModelBackend):
    def authenticate(self, request, user) -> DiscordUser:
        find_user = DiscordUser.objects.filter(id=user['id'])
        if len(find_user) == 0:
            print("User was not found. Saving...")
            discord_tag = '%s#%s' % (user['username'], user['discriminator'])
            new_user = DiscordUser.objects.create(
                id= user["id"],
                discord_tag= discord_tag,
                avatar= user["avatar"],
                discriminator= user["discriminator"],
                public_flags= user["public_flags"],
                flags= user["flags"],
                locale= user["locale"],
                mfa_enabled= user["mfa_enabled"]
            )
            print("created")
            return new_user
        return find_user
    
    def get_user(self, user_id):
        try:
            return DiscordUser.objects.get(pk=user_id)
        except DiscordUser.DoesNotExist:
            return None