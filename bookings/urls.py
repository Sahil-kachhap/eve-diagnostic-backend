from django.urls import path

from .views import (
    BookingCancelView,
    BookingCreateView,
    BookingDetailView,
    BookingListCreateView
)

urlpatterns = [
    path(
        "create/",
        BookingCreateView.as_view(),
        name="booking-create",
    ),
    path(
        "",
        BookingListCreateView.as_view(),
        name="booking-list-create",
    ),
    path(
        "<int:pk>/",
        BookingDetailView.as_view(),
        name="booking-detail",
    ),
    path(
        "<int:pk>/cancel/",
        BookingCancelView.as_view(),
        name="booking-cancel",
    ),
]
