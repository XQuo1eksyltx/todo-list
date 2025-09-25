# apps/ToDoList_app/services.py
from typing import Optional
from django.db import transaction
from .domain.models import Task, Tag

@transaction.atomic
def change_title(*, task: Task, title: str) -> Task:
    task.title = title
    task.save(update_fields=["title"])
    return task

@transaction.atomic
def toggle_task_done(*, task: Task) -> Task:
    task.is_done = not task.is_done
    task.save(update_fields=["is_done"])
    return task

@transaction.atomic
def add_tag_to_task(*, task: Task, tag_id: Optional[int] = None, tag_name: Optional[str] = None) -> Task:
    if tag_id is None and not tag_name:
        raise ValueError("Either tag_id or tag_name is required")

    if tag_id is not None:
        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            raise ValueError("Tag not found")
    else:
        tag, _ = Tag.objects.get_or_create(name=tag_name)

    task.tags.add(tag)  # идемпотентно для M2M
    return task

@transaction.atomic
def delete_tag_from_task(*, task: Task, tag_id: int) -> None:
    if not isinstance(tag_id, int):
        raise ValueError("tag_id must be integer")
    try:
        tag = Tag.objects.get(pk=tag_id)
    except Tag.DoesNotExist:
        raise ValueError("Tag not found")
    task.tags.remove(tag)
