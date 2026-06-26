from rest_framework import viewsets
from .models import UserDevice, UserLocation, SecurityAlert
from .serializers import UserDeviceSerializer, UserLocationSerializer, SecurityAlertSerializer

class UserDeviceViewSet(viewsets.ModelViewSet):
    queryset = UserDevice.objects.all()
    serializer_class = UserDeviceSerializer

class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer

class SecurityAlertViewSet(viewsets.ModelViewSet):
    queryset = SecurityAlert.objects.all()
    serializer_class = SecurityAlertSerializer
