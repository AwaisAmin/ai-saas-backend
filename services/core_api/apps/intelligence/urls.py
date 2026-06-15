from django.urls import path
from .views import GenerateView, SummarizeView, SuggestView

urlpatterns = [
    path("generate/", GenerateView.as_view(), name="ai-generate"),
    path("summarize/", SummarizeView.as_view(), name="ai-summarize"),
    path("suggest/", SuggestView.as_view(), name="ai-suggest"),
]
