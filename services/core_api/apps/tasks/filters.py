import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Task.StatusChoices.choices)
    priority = django_filters.ChoiceFilter(choices=Task.PriorityChoices.choices)
    assignee = django_filters.UUIDFilter(field_name='assignee__id')
    due_date_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    due_date_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')

    class Meta:
        model = Task
        fields = ['status', 'priority', 'assignee', 'due_date_before', 'due_date_after']
