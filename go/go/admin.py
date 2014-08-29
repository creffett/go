from django.contrib import admin
from go.models import URL, RegisteredUser
from moderation.admin import ModerationAdmin

# Register your models here.
admin.site.register(URL)

class RegisteredUserAdmin(ModerationAdmin):
    admin_integration_enabled = True

admin.site.register(RegisteredUser, RegisteredUserAdmin)
