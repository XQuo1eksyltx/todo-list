import django_filters
from apps.ToDoList_app.domain.models import Task

class TaskFilter(django_filters.FilterSet):
    # диапазон по дате дедлайна: ?due_from=2025-09-01&due_to=2025-09-30
    due_from = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_to = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ["is_done", "tags__id"]