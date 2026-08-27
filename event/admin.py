from django.contrib import admin
from event.models import Event, EventComment, EventLike, EventManager

# Register your models here.

class EventAdmin(admin.ModelAdmin):
    pass

admin.site.register(Event)
admin.site.register(EventComment)
admin.site.register(EventLike)