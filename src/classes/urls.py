from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (FitnessClassViewSet, ClassTypeViewSet,
                    LevelViewSet, BookingViewSet)

router = DefaultRouter()
router.register('class-types', ClassTypeViewSet, 'class_types')
router.register('levels', LevelViewSet, basename='levels')
router.register('bookings', BookingViewSet, basename='bookings')
router.register('', FitnessClassViewSet, basename='classes')

urlpatterns = [
    path('', include(router.urls)),
]
