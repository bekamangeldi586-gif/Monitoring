"""
URL routing for sensors_app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sensor-types', views.SensorTypeViewSet, basename='sensor-type')
router.register(r'sensors', views.SensorViewSet, basename='sensor')
router.register(r'readings', views.ReadingViewSet, basename='reading')
router.register(r'alerts', views.AlertViewSet, basename='alert')
router.register(r'dashboard', views.DashboardView, basename='dashboard')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.dashboard, name='dashboard'),
]
