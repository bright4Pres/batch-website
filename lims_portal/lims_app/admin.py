from django.contrib import admin
from .models import scholarList, commenter

# Register your models here.
@admin.register(scholarList)
class scholarListAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'section')

@admin.register(commenter)
class commenterAdmin(admin.ModelAdmin):
    list_display = ('username', 'comment', 'targetScholar')