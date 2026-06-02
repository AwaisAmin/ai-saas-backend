from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from common.response import success_response, error_response, format_errors
from common.mixins import OrganizationScopedMixin
from apps.projects.services import ProjectService
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer
from .services import TaskService, CreateTaskInput, UpdateTaskInput

class TaskListCreateView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str, project_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
        except ValueError as e:
            return error_response(message=str(e), status=404)

        tasks = TaskService.get_all(project)
        return success_response(data=TaskSerializer(tasks, many=True).data)

    def post(self, request: Request, slug: str, project_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
        except ValueError as e:
            return error_response(message=str(e), status=404)

        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

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
        return success_response(
            data=TaskSerializer(task).data,
            message="Task created successfully",
            status=201,
        )

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
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

        inp = UpdateTaskInput(
            title=serializer.validated_data.get('title'),
            description=serializer.validated_data.get('description'),
            status=serializer.validated_data.get('status'),
            priority=serializer.validated_data.get('priority'),
            due_date=str(serializer.validated_data['due_date']) if serializer.validated_data.get('due_date') else None,
            assignee_id=str(serializer.validated_data['assignee_id']) if serializer.validated_data.get('assignee_id') else None,
        )
        updated = TaskService.update(task, inp)
        return success_response(
            data=TaskSerializer(updated).data,
            message="Task updated successfully",
        )

    def delete(self, request: Request, slug: str, project_id: str, task_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
            task = TaskService.get_by_id(str(task_id), project)
            TaskService.delete(task)
            return success_response(message="Task deleted successfully")
        except ValueError as e:
            return error_response(message=str(e), status=404)
