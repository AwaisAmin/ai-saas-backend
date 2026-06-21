from django.urls import path
from .views import GenerateView, SummarizeView, SuggestView

urlpatterns = [
    path("generate-tasks/", GenerateView.as_view(), name="ai-generate-tasks"),
    path("summarize-project/", SummarizeView.as_view(), name="ai-summarize-project"),
    path("suggest-assignee/", SuggestView.as_view(), name="ai-suggest-assignee"),
]
