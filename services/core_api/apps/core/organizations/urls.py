from django.urls import path
from .views import (
    BulkInviteView,
    InvitePreviewView,
    InviteRespondView,
    MemberDetailView,
    MemberListInviteView,
    MyPendingInvitesView,
    OrganizationDetailView,
    OrganizationListCreateView,
    SlugCheckView,
)

urlpatterns = [
    path('', OrganizationListCreateView.as_view(), name='org-list-create'),
    path('check-slug/', SlugCheckView.as_view(), name='org-check-slug'),
    path('my-invites/', MyPendingInvitesView.as_view(), name='my-pending-invites'),
    path('invite/preview/', InvitePreviewView.as_view(), name='invite-preview'),
    path('invite/respond/', InviteRespondView.as_view(), name='invite-respond'),
    path('<slug:slug>/', OrganizationDetailView.as_view(), name='org-detail'),
    path('<slug:slug>/members/', MemberListInviteView.as_view(), name='org-members'),
    path('<slug:slug>/members/bulk-invite/', BulkInviteView.as_view(), name='org-bulk-invite'),
    path('<slug:slug>/members/<uuid:membership_id>/', MemberDetailView.as_view(), name='org-member-detail'),
]
