from django.contrib import admin

from . import models

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'difficulty_level', 'image')  # Добавили отображение изображения в админке
    search_fields = ('title', 'description')


# Register your models here.
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Topic)
admin.site.register(models.Lesson)

