from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import CommentForm
from .models import Course, Topic, Lesson, CourseProgress
import markdown
from django.utils.safestring import mark_safe
from django.http import Http404, HttpResponseNotFound


def course_main_page(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'courses.html', context)


###############################################################

@login_required
def start_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if not course.topics.exists():
        raise Http404("404 Ошибка: У этого курса нет тем.")

    # Проверяем прогресс пользователя
    try:
        user_progress = CourseProgress.objects.get(user=request.user, course=course)
        last_lesson = user_progress.last_lesson
        if last_lesson:
            return redirect('single_lesson', lesson_id=last_lesson.id)
    except CourseProgress.DoesNotExist:
        pass  # Если нет прогресса, отправляем на первый урок

    first_lesson = course.topics.first().lessons.first() if course.topics.exists() else None

    if first_lesson:
        return redirect('single_lesson', lesson_id=first_lesson.id)
    else:
        raise Http404("404 Ошибка: В этом курсе еще нет уроков.")


def single_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.topic.course

    # Обновление прогресса пользователя
    user_progress, created = CourseProgress.objects.get_or_create(user=request.user, course=course)
    user_progress.last_lesson = lesson
    user_progress.save()

    # Получение всех тем курса, отсортированных по порядку
    topics = list(course.topics.all())
    current_topic_index = topics.index(lesson.topic)
    current_lesson_index = list(lesson.topic.lessons.all()).index(lesson)

    # Определение предыдущего урока
    previous_lesson = None
    if current_lesson_index > 0:
        previous_lesson = lesson.topic.lessons.all()[current_lesson_index - 1]
    else:
        if current_topic_index > 0:
            previous_topic = topics[current_topic_index - 1]
            previous_lesson = previous_topic.lessons.last()

    # Определение следующего урока
    next_lesson = None
    if current_lesson_index < lesson.topic.lessons.count() - 1:
        next_lesson = lesson.topic.lessons.all()[current_lesson_index + 1]
    else:
        if current_topic_index < len(topics) - 1:
            next_topic = topics[current_topic_index + 1]
            next_lesson = next_topic.lessons.first()

    lesson_content_html = mark_safe(markdown.markdown(lesson.content, extensions=['fenced_code', 'codehilite']))

    context = {
        'course': course,
        'lesson': lesson,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'is_first_lesson': previous_lesson is None,
        'lesson_content_html': lesson_content_html,
    }
    return render(request, 'course_area.html', context)


###############################################################
"""Обрабатывает добавление комментария."""


def single_course(request, course_id):
    # Получаем объект курса или возвращаем 404
    course = get_object_or_404(Course, pk=course_id)

    # Обрабатываем форму комментария
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            # Сохраняем комментарий
            comment = form.save(commit=False)
            comment.user = request.user
            comment.course = course
            comment.save()

            # Перенаправляем пользователя на ту же страницу (PRG паттерн)
            return redirect('single_course', course_id=course.id)
    else:
        form = CommentForm()

    # Получаем только 10 последних комментариев
    comments = course.comments.all().order_by('-created_at')[:10]

    # Передаём данные в шаблон
    context = {
        'course': course,
        'form': form,
        'comments': comments,
    }
    return render(request, 'single_course.html', context)
