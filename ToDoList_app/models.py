from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#tags
class Tag(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f'{self.name}'

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_done = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)

    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)

    @property
    def public_id(self):
        return f"T-{self.id + 20000:X}"

    def __str__(self):
        return f'{self.created_at.strftime("%m/%d/%Y")} {self.title}'

