from django.contrib import admin

from football365.models import Call


class CallAdmin(admin.ModelAdmin):
    list_display = ('title', 'call_type', 'football365_di')

admin.site.register(Call, CallAdmin)
