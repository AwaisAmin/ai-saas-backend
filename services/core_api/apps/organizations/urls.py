from django.urls import path
from .views import (
    OrganizationListCreateView,
    OrganizationDetailView,
    MemberListInviteView,
    MemberDetailView,
)

urlpatterns = [
    path('', OrganizationListCreateView.as_view(), name='org-list-create'),
    path('<slug:slug>/', OrganizationDetailView.as_view(), name='org-detail'),
    path('<slug:slug>/members/', MemberListInviteView.as_view(), name='org-members'),
    path('<slug:slug>/members/<uuid:membership_id>/', MemberDetailView.as_view(), name='org-member-detail'),
]
