from django.urls import path, include
from credit.views import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),  # Render HTML
    path("api/", include("credit.urls")),   # All APIs under /api/
]