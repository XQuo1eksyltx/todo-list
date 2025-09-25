from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

TASK_FILTER_PARAMS = [
    OpenApiParameter("is_done", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                     description="Фильтр по статусу"),
    OpenApiParameter("tags__id", OpenApiTypes.INT, OpenApiParameter.QUERY,
                     description="Фильтр по ID тега"),
    OpenApiParameter("due_from", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                     description="Дедлайн с (YYYY-MM-DD)"),
    OpenApiParameter("due_to", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                     description="Дедлайн по (YYYY-MM-DD)"),
    OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY,
                     description="Поиск по title"),
    OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY,
                     description="Сортировка: id, -id, due_date, -due_date, created_at, -created_at"),
]

DELETE_TAG_PARAMS = [
    OpenApiParameter(
        name="tag_id",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=True,
        description="ID тега, который отвязать от задачи",
    ),
]