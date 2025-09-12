from rest_framework import serializers
from .models import Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "is_done"]

class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = ['user', 'id', 'title', 'is_done', 'created_at', 'updated_at', 'due_date', 'tags']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def _val(self, attrs, name, default=None):
        if name in attrs:
            return attrs[name]
        if self.instance is not None:
            return getattr(self.instance, name, default)
        return default

    def validate(self, attrs):
        is_done = self._val(attrs, "is_done", False)
        due_date = self._val(attrs, "due_date")

        if is_done and not due_date:
            raise serializers.ValidationError({"due_date": "Required if task is completed"})
        return attrs


    def validate_title(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("Task title can't be empty")
        if len(v) > 120:
            raise serializers.ValidationError("Task title can't be longer than 120 characters")
        return v

class TaskChangeTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title"]

    def validate_title(self, v):
        if not v or not v.strip():
            raise serializers.ValidationError("Title can't be empty.")
        return v

class TaskCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["is_done"]
        read_only_fields = ["is_done"]

    def validate_is_done(self, v):
        if v is not True:
            raise serializers.ValidationError("Set is_done=true to complete the task.")
        return v

class TaskStatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    done_count = serializers.IntegerField()
    percent = serializers.FloatField()

class TaskAddTagInput(serializers.Serializer):
    tag_id = serializers.IntegerField(required=False)
    tag_name = serializers.CharField(required=False)

    def validate(self, attrs):
        tag_id = attrs.get("tag_id")
        tag_name = (attrs.get("tag_name") or "").strip()

        if not tag_id and not tag_name:
            raise serializers.ValidationError("Provide either 'tag_id' or 'tag_name'.")
        if tag_id and tag_name:
            raise serializers.ValidationError("Use only one of: 'tag_id' or 'tag_name'.")
        attrs["tag_name"] = tag_name
        return attrs


