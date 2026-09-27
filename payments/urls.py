from django.urls import path

from .views import PaymentCreateView


urlpatterns = [
    path(
        "",
        PaymentCreateView.as_view(),
        name="payment-create",
    ),
]