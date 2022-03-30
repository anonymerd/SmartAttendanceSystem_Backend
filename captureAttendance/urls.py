# from rest_framework import routers
# from .api import ImageViewSet
from .views import ImageAPIView, EmployeeAPIView
from django.urls import path
# router = routers.DefaultRouter()
# router.register('api/image', ImageViewSet, 'image')

urlpatterns = [
    path('api/image/', ImageAPIView.as_view(), name='image'),
    path('api/employee/', EmployeeAPIView.as_view(), name='employee')
]
