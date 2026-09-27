from rest_framework import generics
from accounts.permissions import IsAdminUserRole
from .models import DiagnosticCentre, DiagnosticTest, CentreTest
from .serializers import DiagnosticCentreSerializer, DiagnosticTestSerializer, CentreTestSerializer


class DiagnosticCentreListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUserRole()]
        return super().get_permissions()


class DiagnosticCentreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUserRole()]
        return super().get_permissions()


class DiagnosticTestListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUserRole()]
        return super().get_permissions()


class DiagnosticTestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUserRole()]
        return super().get_permissions()

class CentreTestListCreateView(generics.ListCreateAPIView):
    queryset = CentreTest.objects.select_related(
        "centre",
        "test",
    )
    serializer_class = CentreTestSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUserRole()]
        return super().get_permissions()


class CentreTestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CentreTest.objects.select_related(
        "centre",
        "test",
    )
    serializer_class = CentreTestSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUserRole()]
        return super().get_permissions()

class AvailableCentreTestListView(generics.ListAPIView):
    serializer_class = CentreTestSerializer

    def get_queryset(self):
        return (
            CentreTest.objects
            .filter(is_available=True)
            .select_related("centre", "test")
        )