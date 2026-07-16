from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.core.organizations.models import Membership
from apps.workspace.activity.models import ActivityLog
from common.activity import queue_activity
from common.mixins import OrganizationScopedMixin
from common.response import error_response, format_errors, success_response

from .serializers import TaskCreateSerializer, TaskSerializer, TaskUpdateSerializer
from .services import CreateTaskInput, TaskService, UpdateTaskInput
from apps.workspace.projects.services import ProjectService


class TaskListCreateView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request: Request, slug: str, project_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
        except ValueError as e:
            return error_response(message=str(e), status=404)

        tasks = TaskService.get_all(project, filters=request.GET.dict())

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tasks, request)
        return paginator.get_paginated_response(TaskSerializer(page, many=True).data)

    def post(self, request: Request, slug: str, project_id: str):
        org = self.get_organization()
        membership = self.get_membership(org)

        if membership.role == Membership.RoleChoices.VIEWER:
            return error_response(message="Viewers cannot create tasks", status=403)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
        except ValueError as e:
            return error_response(message=str(e), status=404)

        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")

        inp = CreateTaskInput(
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            priority=serializer.validated_data.get('priority', 'medium'),
            due_date=str(serializer.validated_data['due_date']) if serializer.validated_data.get('due_date') else None,
            assignee_id=str(serializer.validated_data['assignee_id']) if serializer.validated_data.get('assignee_id') else None,
            project_id=str(project.id),
            created_by_id=str(request.user.id),
        )
        task = TaskService.create(inp)

        queue_activity(
            org=org, user=request.user,
            action=ActivityLog.ActionChoices.TASK_CREATED,
            entity_type=ActivityLog.EntityTypeChoices.TASK,
            entity_id=task.id,
            metadata={'task_title': task.title, 'project_id': str(project.id), 'priority': task.priority},
        )
        return success_response(data=TaskSerializer(task).data, message="Task created successfully", status=201)


class TaskDetailView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str, project_id: str, task_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
            task = TaskService.get_by_id(str(task_id), project)
            return success_response(data=TaskSerializer(task).data)
        except ValueError as e:
            return error_response(message=str(e), status=404)

    def patch(self, request: Request, slug: str, project_id: str, task_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
            task = TaskService.get_by_id(str(task_id), project)
        except ValueError as e:
            return error_response(message=str(e), status=404)

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")

        inp = UpdateTaskInput(
            title=serializer.validated_data.get('title'),
            description=serializer.validated_data.get('description'),
            status=serializer.validated_data.get('status'),
            priority=serializer.validated_data.get('priority'),
            due_date=str(serializer.validated_data['due_date']) if serializer.validated_data.get('due_date') else None,
            assignee_id=str(serializer.validated_data['assignee_id']) if serializer.validated_data.get('assignee_id') else None,
        )
        updated = TaskService.update(task, inp)
        return success_response(data=TaskSerializer(updated).data, message="Task updated successfully")

    def delete(self, request: Request, slug: str, project_id: str, task_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
            task = TaskService.get_by_id(str(task_id), project)
            TaskService.delete(task)
            queue_activity(
                org=org, user=request.user,
                action=ActivityLog.ActionChoices.TASK_DELETED,
                entity_type=ActivityLog.EntityTypeChoices.TASK,
                entity_id=task.id,
                metadata={'task_title': task.title},
            )
            return success_response(message="Task deleted successfully")
        except ValueError as e:
            return error_response(message=str(e), status=404)
