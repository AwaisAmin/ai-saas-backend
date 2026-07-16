from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from common.response import success_response, error_response, format_errors
from common.mixins import OrganizationScopedMixin
from apps.billing.subscriptions.services import SubscriptionService
from apps.workspace.activity.tasks import log_activity
from apps.workspace.activity.models import ActivityLog
from apps.core.users.models import User
from .models import Project
from .serializers import ProjectSerializer, ProjectCreateSerializer, ProjectUpdateSerializer
from .services import ProjectService, CreateProjectInput, UpdateProjectInput
from common.constants import ADMIN_ROLES

class ProjectListCreateView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str):
        org = self.get_organization()
        self.get_membership(org)
        projects = ProjectService.get_all(org)
        return success_response(data=ProjectSerializer(projects, many=True).data)

    def post(self, request: Request, slug: str):
        org = self.get_organization()
        membership = self.get_membership(org)

        if membership.role not in ADMIN_ROLES:
            return error_response(
                message="Only owner or admin can create projects",
                status=403,
            )

        can_create, message = SubscriptionService.can_create_project(org)
        if not can_create:
            return error_response(message=message, status=403)

        serializer = ProjectCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

        inp = CreateProjectInput(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            template=serializer.validated_data.get('template', 'blank'),
            organization_id=str(org.id),
            owner_id=str(request.user.id),
        )
        project = ProjectService.create(inp)

        if request.user.onboarding_step != User.OnboardingStep.COMPLETED:
            request.user.onboarding_step = User.OnboardingStep.COMPLETED
            request.user.save(update_fields=['onboarding_step', 'updated_at'])

        log_activity.delay(
            organization_id=str(org.id),
            user_id=str(request.user.id),
            action=ActivityLog.ActionChoices.PROJECT_CREATED,
            entity_type=ActivityLog.EntityTypeChoices.PROJECT,
            entity_id=str(project.id),
            metadata={'project_name': project.name, 'template': project.template}
        )
        return success_response(
            data=ProjectSerializer(project).data,
            message="Project created successfully",
            status=201,
        )

class ProjectDetailView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str, project_id: str):
        org = self.get_organization()
        self.get_membership(org)
        try:
            project = ProjectService.get_by_id(str(project_id), org)
            return success_response(data=ProjectSerializer(project).data)
        except ValueError as e:
            return error_response(message=str(e), status=404)

    def patch(self, request: Request, slug: str, project_id: str):
        org = self.get_organization()
        membership = self.get_membership(org)

        if membership.role not in ADMIN_ROLES:
            return error_response(
                message="Only owner or admin can update projects",
                status=403,
            )

        try:
            project = ProjectService.get_by_id(str(project_id), org)
        except ValueError as e:
            return error_response(message=str(e), status=404)

        serializer = ProjectUpdateSerializer(project, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

        inp = UpdateProjectInput(
            name=serializer.validated_data.get('name'),
            description=serializer.validated_data.get('description'),
            status=serializer.validated_data.get('status'),
        )
        updated = ProjectService.update(project, inp)
        log_activity.delay(
            organization_id=str(org.id),
            user_id=str(request.user.id),
            action=ActivityLog.ActionChoices.PROJECT_UPDATED,
            entity_type=ActivityLog.EntityTypeChoices.PROJECT,
            entity_id=str(project.id),
            metadata={'project_name': project.name}
        )
        return success_response(
            data=ProjectSerializer(updated).data,
            message="Project updated successfully",
        )

    def delete(self, request: Request, slug: str, project_id: str):
        org = self.get_organization()
        self.get_membership(org)

        try:
            project = ProjectService.get_by_id(str(project_id), org)
            ProjectService.delete(project, request.user)
            log_activity.delay(
                organization_id=str(org.id),
                user_id=str(request.user.id),
                action=ActivityLog.ActionChoices.PROJECT_DELETED,
                entity_type=ActivityLog.EntityTypeChoices.PROJECT,
                entity_id=str(project.id),
                metadata={'project_name': project.name}
            )
            return success_response(message="Project deleted successfully")
        except ValueError as e:
            return error_response(message=str(e), status=403)
