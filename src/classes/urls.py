from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FitnessClassViewSet, ClassTypeViewSet, LevelViewSet

router = DefaultRouter()
router.register('class-types', ClassTypeViewSet)
router.register('levels', LevelViewSet)
router.register('classes', FitnessClassViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
