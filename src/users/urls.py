from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FitnessProfileViewSet

router = DefaultRouter()
router.register('', UserViewSet)
router.register('profiles', FitnessProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
