from django.urls import path

from .views import CurrentUserView, SignupView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("me/", CurrentUserView.as_view(), name="current_user")
]