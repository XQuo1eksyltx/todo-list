# apps/ToDoList_app/selectors.py
from typing import Dict
from django.db.models import QuerySet
from .domain.models import Task

def tasks_for_user(*, user) -> QuerySet[Task]:
    """Базовый queryset задач пользователя (с сортировкой и префетчем тегов)."""
    qs = Task.objects.filter(user=user).order_by("-id")
    return qs.prefetch_related("tags") if hasattr(Task, "tags") else qs

def task_stats(qs: QuerySet[Task]) -> Dict[str, float | int]:
    """Агрегации по задачам (кол-во/выполненные/процент)."""
    count = qs.count()
    done = qs.filter(is_done=True).count()
    percent = round(done / count * 100.0, 2) if count else 0.0
    return {"count": count, "done_count": done, "percent": percent}

def get_task_tags(*, task: Task):
    """Список тегов у задачи."""
    return task.tags.all()
