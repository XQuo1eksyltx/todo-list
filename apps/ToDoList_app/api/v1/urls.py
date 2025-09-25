from rest_framework.routers import DefaultRouter
from apps.ToDoList_app.api.v1.views import TaskViewSet
router = DefaultRouter()

router.register(r'tasks', TaskViewSet , basename='tasks')

urlpatterns = router.urls