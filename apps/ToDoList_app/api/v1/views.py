from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema

from apps.ToDoList_app.docs import TASK_FILTER_PARAMS, DELETE_TAG_PARAMS
from apps.ToDoList_app.domain.models import Task, Tag  # Tag может понадобиться для queryset фильтров
from apps.ToDoList_app.api.v1.serializers import (
    TaskSerializer, TaskListSerializer,
    TaskChangeTitleSerializer, TaskCompleteSerializer, TaskStatsSerializer,
    TaskAddTagInput, TagSerializer
)
from apps.ToDoList_app.api.v1.permissions import IsOwnerOrReadOnly
from apps.ToDoList_app.api.v1.filters import TaskFilter

# НОВОЕ: импорт слоёв
from apps.ToDoList_app import selectors
from apps.ToDoList_app import services


@extend_schema(parameters=[])
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()  # DRF требует атрибут, но фактически используем get_queryset()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filterset_class = TaskFilter

    # filters
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "is_done": ["exact"],
        "due_date": ["exact", "gte", "lte"],
        "tags__id": ["exact"],
    }
    search_fields = ["title"]
    ordering_fields = ["id", "due_date", "created_at"]
    ordering = ["-id"]

    # мапа action → сериализатор
    action_serializers = {
        "list": TaskListSerializer,
        "retrieve": TaskSerializer,
        "change_title": TaskChangeTitleSerializer,
        "complete": TaskCompleteSerializer,
        "stats": TaskStatsSerializer,
        "add_tag": TaskAddTagInput,
    }

    # мапа action → пермишены
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

    # ← теперь строим qs через селектор
    def get_queryset(self):
        return selectors.tasks_for_user(user=self.request.user)

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, TaskSerializer)

    def get_permissions(self):
        classes = self.action_permissions.get(self.action, [IsAuthenticated])
        return [cls() for cls in classes]

    # ---- кастомные действия ----

    @extend_schema(parameters=TASK_FILTER_PARAMS)
    @action(detail=False, methods=["get"])
    def get_all_tasks_and_their_info(self, request, pk=None):
        qs = self.filter_queryset(self.get_queryset())  # фильтры DRF поверх нашего базового qs
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def change_title(self, request, pk=None):
        task = self.get_object()
        ser = self.get_serializer(instance=task, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        # бизнес-логика — в сервис
        task = services.change_title(task=task, title=ser.validated_data["title"])
        return Response(TaskSerializer(task, context=self.get_serializer_context()).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        task = self.get_object()
        task = services.toggle_task_done(task=task)
        return Response(TaskSerializer(task, context=self.get_serializer_context()).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def stats(self, request, pk=None):
        qs = self.get_queryset()
        payload = selectors.task_stats(qs)
        ser = self.get_serializer(instance=payload)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], serializer_class=TaskAddTagInput)
    def add_tag(self, request, pk=None):
        task = self.get_object()
        inp = self.get_serializer(data=request.data)
        inp.is_valid(raise_exception=True)

        try:
            task = services.add_tag_to_task(
                task=task,
                tag_id=inp.validated_data.get("tag_id"),
                tag_name=inp.validated_data.get("tag_name"),
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        out = TaskSerializer(task, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def list_tags(self, request, pk=None):
        task = self.get_object()
        tags = selectors.get_task_tags(task=task)
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(parameters=DELETE_TAG_PARAMS)
    @action(detail=True, methods=["delete"], url_path="delete_tag")
    def delete_tag(self, request, pk=None):
        task = self.get_object()
        tag_id = request.query_params.get("tag_id")

        if tag_id is None:
            return Response({"error": "tag_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tag_id_int = int(tag_id)
        except ValueError:
            return Response({"error": "tag_id must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            services.delete_tag_from_task(task=task, tag_id=tag_id_int)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
