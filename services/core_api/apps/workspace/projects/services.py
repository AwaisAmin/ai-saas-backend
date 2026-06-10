from pydantic import BaseModel as PydanticModel
from .models import Project
from apps.core.organizations.models import Organization
from apps.core.users.models import User

class CreateProjectInput(PydanticModel):
    name: str
    description: str = ""
    organization_id: str
    owner_id: str

class UpdateProjectInput(PydanticModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None

class ProjectService:
    @staticmethod
    def get_all(organization: Organization):
        return Project.objects.filter(
            organization=organization,
        ).select_related('owner')

    @staticmethod
    def get_by_id(project_id: str, organization: Organization) -> Project:
        try:
            return Project.objects.select_related('owner').get(
                id=project_id,
                organization=organization,
            )
        except Project.DoesNotExist:
            raise ValueError("Project not found")

    @staticmethod
    def create(data: CreateProjectInput) -> Project:
        return Project.objects.create(
            name=data.name,
            description=data.description,
            organization_id=data.organization_id,
            owner_id=data.owner_id,
        )

    @staticmethod
    def update(project: Project, data: UpdateProjectInput) -> Project:
        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        if data.status is not None:
            project.status = data.status

        project.save()
        return project

    @staticmethod
    def delete(project: Project, requesting_user: User) -> None:
        from apps.core.organizations.models import Membership
        membership = Membership.objects.get(
            user=requesting_user,
            organization=project.organization,
        )
        if membership.role not in ['owner', 'admin']:
            raise ValueError("Only owner or admin can delete a project")

        project.delete()
