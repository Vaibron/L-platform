from django.shortcuts import render, get_object_or_404, redirect
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
    context = {
        'course': course,
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
