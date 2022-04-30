from itertools import count
from re import S
from rest_framework import serializers
from captureAttendance.models import Company, User, Log, Image
from drf_extra_fields.fields import Base64ImageField


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Image
        fields = ['image']

    def create(self, validated_data):
        image = validated_data.pop('image')
        return Image.objects.create(image=image)


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['companyId', 'name', 'email', 'image', 'city', 'country']

    def create(self, validated_data):
        company = Company(
            companyId=validated_data.pop('companyId'),
            name=validated_data.pop('name'),
            email=validated_data.pop('email'),
            image=validated_data.pop('image'),
            city=validated_data.pop('city'),
            country=validated_data.pop('country')
        )
        company.save()
        return company


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['userId', 'name', 'email', 'password',
                  'companyId', 'image', 'userType', 'designation']

    def create(self, validated_data):
        user = User(
            userId=validated_data.pop('userId'),
            name=validated_data.pop('name'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            companyId=validated_data.pop('companyId'),
            image=validated_data.pop('image'),
            userType=validated_data.pop('userType'),
            designation=validated_data.pop('designation'),
        )
        user.save()
        return user


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = ['userId', 'companyId', 'type', 'datetime', 'location']

    def create(self, validated_data):
        log = Log(
            empId=validated_data.pop('empId'),
            companyId=validated_data.pop('companyId'),
            type=validated_data.pop('type'),
            datetime=validated_data.pop('datetime'),
            location=validated_data.pop('location'),
        )
        log.save()
        return log
