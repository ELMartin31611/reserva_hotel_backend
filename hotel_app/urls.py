from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hotel_app.views.health import health_check

router = DefaultRouter()

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]