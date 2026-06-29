from pydantic import BaseModel as PydanticModel
from .models import Project, ProjectColumn
from apps.core.organizations.models import Organization
from apps.core.users.models import User

TEMPLATE_COLUMNS = {
    'product_sprint':     ['Backlog', 'Todo', 'In Progress', 'In Review', 'Done'],
    'marketing_campaign': ['Ideas', 'Brief', 'In Progress', 'Review', 'Published'],
    'design_agency':      ['Research', 'Design', 'Review', 'Client Review', 'Delivered'],
    'blank':              ['To Do', 'In Progress', 'Done'],
}

class CreateProjectInput(PydanticModel):
    name: str
    description: str = ""
    template: str = "blank"
    organization_id: str
    owner_id: str

class UpdateProjectInput(PydanticModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None

class ProjectService:
    @staticmethod
    def get_all(organization: Organization):
        return (
            Project.objects
            .filter(organization=organization)
            .select_related('owner')
            .prefetch_related('columns')
        )

    @staticmethod
    def get_by_id(project_id: str, organization: Organization) -> Project:
        try:
            return (
                Project.objects
                .select_related('owner')
                .prefetch_related('columns')
                .get(id=project_id, organization=organization)
            )
        except Project.DoesNotExist:
            raise ValueError("Project not found")

    @staticmethod
    def create(data: CreateProjectInput) -> Project:
        template = data.template if data.template in TEMPLATE_COLUMNS else 'blank'

        project = Project.objects.create(
            name=data.name,
            description=data.description,
            template=template,
            organization_id=data.organization_id,
            owner_id=data.owner_id,
        )

        columns = TEMPLATE_COLUMNS[template]
        ProjectColumn.objects.bulk_create([
            ProjectColumn(project=project, name=name, order=i)
            for i, name in enumerate(columns)
        ])

        return project

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
