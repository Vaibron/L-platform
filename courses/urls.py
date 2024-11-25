from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.course_main_page, name='course_list'),
    path('<int:course_id>/', views.single_course, name='single_course'),
    path('start/<int:course_id>/', views.start_course, name='start_course'),
    path('lesson/<int:lesson_id>/', views.single_lesson, name='single_lesson'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
