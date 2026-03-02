from django.contrib import admin
from .models import scholarList, commenter, PrivateMessage

# Register your models here.
@admin.register(scholarList)
class scholarListAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'section')

@admin.register(commenter)
class commenterAdmin(admin.ModelAdmin):
    list_display = ('username', 'comment', 'targetScholar', 'created_at')

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'targetScholar', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'targetScholar')
    search_fields = ('sender_name', 'targetScholar', 'message')