from itsdangerous import Serializer
from captureAttendance.models import Image
from rest_framework import viewsets, permissions
from .serializers import ImageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageViewSet(viewsets.ModelViewSet):

    queryset = Image.objects.all()
    permissions_classes = [permissions.AllowAny]
    serializer_class = ImageSerializer

    def dataDikhao(self):
        print(Image.objects.all())

    def list(self, request):
        queryset = Image.objects.all()
        serializer = ImageSerializer(queryset, many=True)
        print(serializer.data)
        return Response(serializer.data)
