from django.contrib import admin
from . import models

class CourseFilter(admin.SimpleListFilter):
    title = 'курс'  # Название фильтра
    parameter_name = 'course'  # Параметр в URL

    def lookups(self, request, model_admin):
        # Получаем все курсы
        courses = models.Course.objects.all()
        return [(course.id, course.title) for course in courses]

    def queryset(self, request, queryset):
        # Если фильтр выбран, показываем только объекты, связанные с этим курсом
        if self.value():
            if hasattr(queryset.model, 'topic'):  # Проверяем, есть ли у модели связь с темами
                return queryset.filter(topic__course_id=self.value())  # Фильтруем через тему
            elif hasattr(queryset.model, 'course'):  # Проверяем, есть ли у модели связь с курсом напрямую
                return queryset.filter(course_id=self.value())  # Фильтруем напрямую по курсу
        return queryset


# Класс для админки комментариев
class CommentAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'text', 'created_at')  # Отображаем курс, пользователя, текст и дату
    search_fields = ('text', 'user__username')  # Поиск по тексту и имени пользователя
    list_filter = (CourseFilter,)  # Добавляем фильтр по курсу


# Класс для админки курсов
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_available','is_content_available', 'allow_comments', 'show_comments')
    list_filter = ('is_available', 'allow_comments', 'show_comments')
    search_fields = ('title', 'description')


# Класс для админки тем
class TopicAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'order')  # Добавляем отображение поля order
    search_fields = ('title',)  # Поиск по названию темы
    list_filter = ('course',)  # Фильтрация по курсу
    ordering = ('course', 'order')  # Сортировка по курсу и порядку


# Класс для админки уроков
class LessonAdmin(admin.ModelAdmin):
    list_display = ('topic', 'title', 'order')  # Добавляем отображение поля order
    search_fields = ('title',)  # Поиск по названию урока
    list_filter = (CourseFilter,)  # Добавляем фильтр по курсу
    ordering = ('topic__course', 'topic__order', 'order')  # Сортировка по курсу темы, порядку темы и порядку урока


# Регистрируем модели
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Comment, CommentAdmin)  # Регистрируем модель комментариев с фильтром
admin.site.register(models.Lesson, LessonAdmin)  # Регистрируем модель уроков с отображением поля order
admin.site.register(models.Topic, TopicAdmin)  # Регистрируем модель тем с отображением поля order
