from django.urls import path

from .views import (
    AvailableCentreTestListView,
    CentreTestDetailView,
    CentreTestListCreateView,
    DiagnosticCentreDetailView,
    DiagnosticCentreListCreateView,
    DiagnosticTestDetailView,
    DiagnosticTestListCreateView
)

urlpatterns = [
    path(
        "centres/",
        DiagnosticCentreListCreateView.as_view(),
        name="centre-list-create",
    ),
    path(
        "centres/<int:pk>/",
        DiagnosticCentreDetailView.as_view(),
        name="centre-detail",
    ),
    path(
        "tests/",
        DiagnosticTestListCreateView.as_view(),
        name="test-list-create",
    ),
    path(
        "tests/<int:pk>/",
        DiagnosticTestDetailView.as_view(),
        name="test-detail",
    ),
    path(
        "centre-tests/",
        CentreTestListCreateView.as_view(),
        name="centre-test-list-create",
    ),
    path(
        "centre-tests/<int:pk>/",
        CentreTestDetailView.as_view(),
        name="centre-test-detail",
    ),
    path(
        "available-tests/",
        AvailableCentreTestListView.as_view(),
        name="available-tests",
    ),
]
