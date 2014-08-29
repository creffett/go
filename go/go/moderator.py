from moderation import moderation
from go.models import RegisteredUser

from moderation.moderator import GenericModerator

class RegisteredUserModerator(GenericModerator):
    notify_user = False

moderation.register(RegisteredUser, RegisteredUserModerator)
