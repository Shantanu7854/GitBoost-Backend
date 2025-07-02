from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: JsonResponse({"status": "API is running"})),
    path("api/", include("api.urls")),
]
