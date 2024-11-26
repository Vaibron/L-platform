from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import CommentForm
from .models import Course, Topic, Lesson
import markdown
from django.utils.safestring import mark_safe
from django.http import Http404, HttpResponseNotFound


def course_main_page(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'courses.html', context)


def single_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    # Обработка комментария
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user  # Сохраняем пользователя, который оставил комментарий
            comment.course = course  # Привязываем комментарий к курсу
            comment.save()
            return redirect('single_course',
                            course_id=course.id)  # Перезагружаем страницу курса после сохранения комментария
    else:
        form = CommentForm()

    # Получаем все комментарии к курсу
    comments_list = course.comments.all()

    # Пагинация: показываем по 5 комментариев на странице
    paginator = Paginator(comments_list, 5)  # 5 комментариев на странице
    page_number = request.GET.get('page')  # Получаем номер страницы из GET параметров
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы

    context = {
        'course': course,
        'form': form,
        'page_obj': page_obj,  # Передаем объект страницы в контекст
    }
    return render(request, 'single_course.html', context)


def start_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if not course.topics.exists():
        raise Http404("404 Ошибка: У этого курса нет тем.")

    first_lesson = course.topics.first().lessons.first() if course.topics.exists() else None

    if first_lesson:
        return redirect('single_lesson', lesson_id=first_lesson.id)
    else:
        raise Http404("404 Ошибка: В этом курсе еще нет уроков.")


def single_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.topic.course

    # Получение всех тем курса, отсортированных по порядку
    topics = list(course.topics.all())
    current_topic_index = topics.index(lesson.topic)
    current_lesson_index = list(lesson.topic.lessons.all()).index(lesson)

    # Определение предыдущего урока
    previous_lesson = None
    if current_lesson_index > 0:
        previous_lesson = lesson.topic.lessons.all()[current_lesson_index - 1]
    else:
        # Если это первый урок в теме, ищем последний урок в предыдущей теме
        if current_topic_index > 0:
            previous_topic = topics[current_topic_index - 1]
            previous_lesson = previous_topic.lessons.last()

    # Определение следующего урока
    next_lesson = None
    if current_lesson_index < lesson.topic.lessons.count() - 1:
        next_lesson = lesson.topic.lessons.all()[current_lesson_index + 1]
    else:
        # Если это последний урок в теме, ищем первый урок следующей темы
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
