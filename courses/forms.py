from django import forms
from .models import Topic, Lesson

class TopicOrderForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['order']

class LessonOrderForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['order']
