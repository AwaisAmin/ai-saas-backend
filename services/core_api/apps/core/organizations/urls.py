from django.urls import path
from .views import (
    BulkInviteView,
    InvitePreviewView,
    MemberDetailView,
    MemberListInviteView,
    OrganizationDetailView,
    OrganizationListCreateView,
    SlugCheckView,
)

urlpatterns = [
    path('', OrganizationListCreateView.as_view(), name='org-list-create'),
    path('check-slug/', SlugCheckView.as_view(), name='org-check-slug'),
    path('invite/preview/', InvitePreviewView.as_view(), name='invite-preview'),
    path('<slug:slug>/', OrganizationDetailView.as_view(), name='org-detail'),
    path('<slug:slug>/members/', MemberListInviteView.as_view(), name='org-members'),
    path('<slug:slug>/members/bulk-invite/', BulkInviteView.as_view(), name='org-bulk-invite'),
    path('<slug:slug>/members/<uuid:membership_id>/', MemberDetailView.as_view(), name='org-member-detail'),
]
