from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name='Изображение')
    duration = models.CharField(max_length=100, default='Не указано', verbose_name='Длительность')
    difficulty_level = models.CharField(max_length=100, default='Не указан', verbose_name='Уровень сложности')
    is_available = models.BooleanField(default=False, verbose_name='Курс доступен')
    is_content_available = models.BooleanField(default=True, verbose_name='Содержание доступно')
    allow_comments = models.BooleanField(default=True, verbose_name='Разрешить комментарии')
    show_comments = models.BooleanField(default=True, verbose_name='Показывать комментарии')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics', verbose_name='Курс')
    title = models.CharField(max_length=255, verbose_name='Название')
    order = models.PositiveIntegerField(verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')  # Уникальность order в рамках курса
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'

    def __str__(self):
        return f'{self.course} - {self.title}'

    def clean(self):
        # Проверка на значение order
        if self.order <= 0:
            raise ValidationError('Порядок должен быть больше 0.')


class Lesson(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons', verbose_name='Тема')
    title = models.CharField(max_length=255, verbose_name='Название')
    content = models.TextField(verbose_name='Контент')
    video_code = models.CharField(blank=True, verbose_name='Код видео')
    order = models.PositiveIntegerField(verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        unique_together = ('topic', 'order')  # Уникальность order в рамках темы
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return f'{self.topic} - {self.title}'

    def clean(self):
        # Проверка на значение order
        if self.order <= 0:
            raise ValidationError('Порядок должен быть больше 0.')


# Новая модель для комментариев
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, related_name='comments', on_delete=models.CASCADE, verbose_name='Курс')
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Комментарий от {self.user.username} на курс {self.course.title}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']


class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    last_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    progress = models.FloatField(default=0.0)  # Процент завершения курса, можно использовать по желанию

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"