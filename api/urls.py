from django.urls import path
from .views import analyze_github

urlpatterns = [
    path("analyze/", analyze_github),
]
