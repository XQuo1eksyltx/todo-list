from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task, Tag
from .serializers import (
    TaskSerializer, TaskListSerializer,
    TaskChangeTitleSerializer, TaskCompleteSerializer, TaskStatsSerializer, TaskAddTagInput, TagSerializer
)
from .permissions import IsOwnerOrReadOnly


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # Мапа action → сериализатор
    action_serializers = {
        "list": TaskListSerializer,
        "retrieve": TaskSerializer,
        "change_title": TaskChangeTitleSerializer,
        "complete": TaskCompleteSerializer,
        "stats": TaskStatsSerializer,
        "add_tag": TaskAddTagInput,
    }

    # Мапа action → пермишены
    action_permissions = {
        "list": [IsAuthenticated],
        "retrieve": [IsAuthenticated],
        "create": [IsAuthenticated],
        "update": [IsAuthenticated, IsOwnerOrReadOnly],
        "partial_update": [IsAuthenticated, IsOwnerOrReadOnly],
        "destroy": [IsAuthenticated, IsOwnerOrReadOnly],
        "change_title": [IsAuthenticated, IsOwnerOrReadOnly],
        "complete": [IsAuthenticated, IsOwnerOrReadOnly],
        "stats": [IsAuthenticated],
        "add_tag": [IsAuthenticated, IsOwnerOrReadOnly],
    }

    def get_queryset(self):
        # показываем только свои задачи + префетч если есть M2M
        qs = Task.objects.filter(user=self.request.user).order_by("-id")
        return qs.prefetch_related("tags") if hasattr(Task, "tags") else qs

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, TaskSerializer)

    def get_permissions(self):
        classes = self.action_permissions.get(self.action, [IsAuthenticated])
        return [cls() for cls in classes]

    # ---- Кастомные действия: с валидацией и кодами ----

    @action(detail=True, methods=["post"])
    def change_title(self, request, pk=None):
        task = self.get_object()  # 404 и проверка queryset + object perms
        serializer = self.get_serializer(instance=task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        serializer = self.get_serializer(instance=task, data={"is_done": True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def stats(self, request, pk=None):
        qs = self.get_queryset()
        count = qs.count()
        done = qs.filter(is_done=True).count()
        percent = (done / count * 100.0) if count else 0.0
        data = {"count":count, "done_count":done, "percent": round(percent, 2)}
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=TaskAddTagInput)
    def add_tag(self, request, pk=None):
        task = self.get_object()  # учитывает get_queryset() и пермишены

        inp = self.get_serializer(data=request.data)
        inp.is_valid(raise_exception=True)
        tag_id = inp.validated_data.get("tag_id")
        tag_name = inp.validated_data.get("tag_name")

        if tag_id:
            tag = get_object_or_404(Tag, pk=tag_id)
        else:
            tag, _ = Tag.objects.get_or_create(name=tag_name)

        # add() идемпотентен для M2M — дубликаты не создаст
        task.tags.add(tag)

        out = TaskSerializer(task, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def list_tags(self, request, pk=None):
        """
        Вернуть список тегов, привязанных к задаче
        """
        task = self.get_object()
        tags = task.tags.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_urgent(self, request, pk=None):
        task = self.get_object()
        task.priority = "urgent"
        task.save()
        serializer = TaskSerializer(task, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)