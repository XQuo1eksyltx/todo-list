from django.contrib import admin
from apps.ToDoList_app.domain.models import Task, Tag

# Register your models here.
admin.site.register(Task)
admin.site.register(Tag)
