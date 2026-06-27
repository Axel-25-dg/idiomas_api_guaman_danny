from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserDeviceViewSet, UserLocationViewSet, SecurityAlertViewSet

router = DefaultRouter()
router.register(r'devices', UserDeviceViewSet)
router.register(r'locations', UserLocationViewSet)
router.register(r'alerts', SecurityAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
