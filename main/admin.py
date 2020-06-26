from django.contrib import admin
from .models import Student, Visit, Face, Security, BotUser

admin.site.register(Student)
admin.site.register(Visit)
admin.site.register(Face)
admin.site.register(Security)
admin.site.register(BotUser)