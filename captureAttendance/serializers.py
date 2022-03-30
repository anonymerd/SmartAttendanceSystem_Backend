from rest_framework import serializers
from captureAttendance.models import Image, Employee
from drf_extra_fields.fields import Base64ImageField


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        migrate = False
        model = Image
        fields = ['image']

    def create(self, validated_data):
        image = validated_data.pop('image')
        return Image.objects.create(image=image)


class EmployeeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Employee
        fields = ['empId', 'name', 'image']

    def create(self, validated_data):
        image = validated_data.pop('image')
        name = validated_data.pop('name')
        empId = validated_data.pop('empId')
        return Employee.objects.create(name=name, image=image, empId=empId)
