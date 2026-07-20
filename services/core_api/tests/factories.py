import uuid
import factory
from django.utils import timezone
from datetime import timedelta
from factory.django import DjangoModelFactory
from faker import Faker
from apps.core.users.models import User
from apps.core.organizations.models import Organization, Membership, PendingInvite
from apps.workspace.projects.models import Project
from apps.workspace.tasks.models import Task
from apps.billing.subscriptions.models import Subscription

fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.LazyFunction(lambda: fake.unique.email())
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    is_active = True
    is_verified = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password(extracted or 'TestPass123!')
        self.save()

class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.LazyFunction(lambda: fake.company())
    slug = factory.LazyFunction(lambda: fake.unique.slug())
    is_active = True

class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)
    role = Membership.RoleChoices.OWNER

class PendingInviteFactory(DjangoModelFactory):
    class Meta:
        model = PendingInvite

    organization = factory.SubFactory(OrganizationFactory)
    email = factory.LazyFunction(lambda: fake.unique.email())
    role = Membership.RoleChoices.MEMBER
    token = factory.LazyFunction(uuid.uuid4)
    invited_by = factory.SubFactory(UserFactory)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    is_accepted = False

class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription

    organization = factory.SubFactory(OrganizationFactory)
    plan = Subscription.PlanChoices.FREE
    status = Subscription.StatusChoices.ACTIVE

class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.LazyFunction(lambda: fake.bs())
    status = 'active'

class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    project = factory.SubFactory(ProjectFactory)
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    status = 'todo'
    priority = 'medium'
