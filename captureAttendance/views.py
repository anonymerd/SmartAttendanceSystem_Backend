from yaml import serialize
from captureAttendance.models import Company, User, Log
from rest_framework import viewsets, permissions
from .serializers import CompanySerializer, ImageSerializer, UserSerializer, LogSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import BaseRenderer
from rest_framework_simplejwt.tokens import RefreshToken


import os
import re
import jwt

from deepface import DeepFace
import pandas as pd
import numpy as np


class ImageAPIView(APIView):
    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            # print(os.path.basename(serializer.data['image']))
            img = os.path.basename(serializer.data['image'])

            df = DeepFace.find(img_path='uploads/' + img, db_path="images/",
                               distance_metric='euclidean_l2')
            try:
                os.remove("images/representations_vgg_face.pkl")
            except:
                print("No data to be removed")

            if df is None or df.empty is True:
                print("No match found for given Person")
                return Response("No records found scan again", status=404)
            else:
                print("Match Found")
                sorted_df = df.sort_values(
                    by=['VGG-Face_euclidean_l2'], ascending=False)
                numpyArrOfDF = sorted_df.to_numpy()

                if not np.size(numpyArrOfDF):
                    print("Error: No panda data frames found ")
                    return Response("No records found scan again", status=404)
                if numpyArrOfDF[0][1] < 0.4:
                    print("Error: Euclidean Distance Less then threshold")
                    return Response("No records found scan again", status=404)
                else:

                    fileName = re.split("\/", numpyArrOfDF[0][0], 2)
                    userId = re.split("\.", fileName[2], 1)[0]

                    print("Finding for User with id: " + userId)

                    try:
                        recognizedEmp = User.objects.get(pk=userId)
                        empSerializer = UserSerializer(recognizedEmp)
                        print("Info Matched Emp: ")
                        print(empSerializer.data)
                        return Response(empSerializer.data, status=200)
                    except:
                        print("Error: No match found")
                        return Response("No records found scan again", status=404)

        print("Error: bad request")
        return Response(serializer.errors, status=400)


class UserAPIView(APIView):
    '''
        Performs CRUD operations for User Model
    '''

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                print("Saved User: ")
                print(serializer.data)
                return Response({'status': True, 'data': serializer.data}, status=201)
        except Exception as err:
            print(err)
            return Response({'status': False, 'message': err}, status=400)

    def get(self, request, companyId, userId=None, format=None):

        try:
            if companyId is not None:

                user = None

                if userId is not None:
                    user = User.objects.get(companyId=companyId, userId=userId)
                    serializer = UserSerializer(user)
                    response = {
                        'userId': serializer.data['userId'],
                        'name': serializer.data['name'],
                        'email': serializer.data['email'],
                        'image': serializer.data['image'],
                        'designation': serializer.data['designation'],
                    }
                    return Response({'status': True, 'data': response}, status=200)
                else:
                    users = User.objects.filter(companyId=companyId)
                    ids = [user.userId for user in users]

                    return Response({'status': True, 'data': ids}, status=200)
            else:
                return Response({'status': False, 'message': 'Company Id not provided'})
        except User.DoesNotExist:
            return Response({'status': False, 'message': 'User Does not exists'})
        except Exception as err:
            print(err)
            return Response({'status': False, 'message': err}, status=400)

    def delete(self, request, id, format=None):
        try:
            emp = User.objects.get(userId=id)
            serializer = UserSerializer(emp)
            emp.delete()
            return Response({'status': True, 'data': 'User deleted'})
        except Exception as err:
            return Response({'status': False, 'message': err}, status=400)


class CompanyAPIView(APIView):

    def post(self, request):
        try:
            serializer = CompanySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                print('Saved Company')
                return Response(serializer.data, status=201)
        except Exception as err:
            print(err)
            return Response({'status': False, 'message': err}, status=400)


class LogsAPIView(APIView):

    def get(self, request, companyId, userId=None, format=None):
        try:
            if companyId is not None:

                log = None

                if userId is not None:
                    log = Log.objects.filter(
                        companyId=companyId, userId=userId)

                else:
                    log = Log.objects.filter(companyId=companyId)

                serializer = LogSerializer(log, many=True)

                return Response({'status': True, 'data': serializer.data})
            else:
                return Response({'status': False, 'message': 'companyId not provided'})

        except Exception as err:
            print(err)
            return Response({'status': False, 'message': err})


class LoginApiView(APIView):
    def post(self, request):
        try:
            # Getting the user for the given email.
            data = request.data
            user = User.objects.get(email=data['email'])

            serializer = UserSerializer(user)
            if data['password'] == serializer.data['password']:
                userData = serializer.data
                refresh = RefreshToken.for_user(user)
                refresh['userId'] = userData['userId']
                refresh['userType'] = userData['userType']
                token = refresh.access_token

                responseData = {
                    'access': str(token),
                    'refresh': str(refresh),
                    'userId': userData['userId']
                }

                return Response({'status': True, 'data': responseData})

            else:
                return Response({'status': False, 'message': 'Incorrect Password'})

            # return Response(serializer.data)

        except User.DoesNotExist:
            return Response({'status': False, 'message': 'User Does Not Exists'})


class RefreshTokenAPIView(APIView):
    def post(self, request):
        token = request.data['token']

        if token is not None:
            refresh = RefreshToken(token)
            token = refresh.access_token

            return Response({'status': True, 'data': {'access': str(token)}})
