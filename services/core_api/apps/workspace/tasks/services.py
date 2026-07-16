from typing import Optional

from pydantic import BaseModel as PydanticModel

from .models import Task
from apps.workspace.projects.models import Project
from apps.core.users.models import User

_ALLOWED_SORT_FIELDS = {'created_at', 'due_date', 'priority', 'title'}


class CreateTaskInput(PydanticModel):
    title: str
    description: str = ""
    priority: str = "medium"
    due_date: Optional[str] = None
    assignee_id: Optional[str] = None
    project_id: str
    created_by_id: str


class UpdateTaskInput(PydanticModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    assignee_id: Optional[str] = None


class TaskService:
    @staticmethod
    def get_all(project: Project, filters: dict = None):
        from .filters import TaskFilter

        queryset = Task.objects.filter(project=project).select_related('created_by', 'assignee')

        if not filters:
            return queryset

        queryset = TaskFilter(filters, queryset=queryset).qs

        if search := filters.get('search'):
            queryset = queryset.filter(title__icontains=search)

        sort_by = filters.get('sort_by', 'created_at')
        if sort_by not in _ALLOWED_SORT_FIELDS:
            sort_by = 'created_at'
        if filters.get('order', 'desc') == 'desc':
            sort_by = f'-{sort_by}'

        return queryset.order_by(sort_by)

    @staticmethod
    def get_by_id(task_id: str, project: Project) -> Task:
        try:
            return Task.objects.select_related('created_by', 'assignee').get(
                id=task_id,
                project=project,
            )
        except Task.DoesNotExist:
            raise ValueError("Task not found")

    @staticmethod
    def create(data: CreateTaskInput) -> Task:
        return Task.objects.create(
            title=data.title,
            description=data.description,
            priority=data.priority,
            due_date=data.due_date,
            assignee_id=data.assignee_id,
            project_id=data.project_id,
            created_by_id=data.created_by_id,
        )

    @staticmethod
    def update(task: Task, data: UpdateTaskInput) -> Task:
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status
        if data.priority is not None:
            task.priority = data.priority
        if data.due_date is not None:
            task.due_date = data.due_date
        if data.assignee_id is not None:
            task.assignee_id = data.assignee_id

        task.save()
        return task

    @staticmethod
    def delete(task: Task) -> None:
        task.delete()
