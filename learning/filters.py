import django_filters
from learning.models import Course, Lesson, UserProgress


class CourseFilter(django_filters.FilterSet):
    difficulty_level = django_filters.CharFilter(lookup_expr='iexact')
    language = django_filters.NumberFilter(field_name='language__id')

    class Meta:
        model = Course
        fields = ['language', 'difficulty_level']


class LessonFilter(django_filters.FilterSet):
    content_type = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Lesson
        fields = ['module', 'content_type']


class UserProgressFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = UserProgress
        fields = ['status', 'lesson']
