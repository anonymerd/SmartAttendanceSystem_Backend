from yaml import serialize
from captureAttendance.models import User, Log, Company
from rest_framework import viewsets, permissions
from .serializers import CompanySerializer, ImageSerializer, UserSerializer, LogSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import BaseRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from .emails import sendMail

# from .faceRecognition import test


import os
import re
import jwt
import string
import random


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
            data = request.data
            user = {
                "userId": data['userId'],
                "name": data['name'],
                "email": data['email'],
                "password": data['password'],
                "companyId": Company.objects.get(companyId=data['companyId']).companyId,
                "image": data['image'],
                "userType": data['userType'],
                "designation": data['designation']
            }
            serializer = UserSerializer(data=user)
            if serializer.is_valid():
                serializer.save()
                print("Saved User: ")
                print(serializer.data)
                return Response({'status': True, 'data': serializer.data}, status=201)
            else:
                return Response(serializer.errors)
        except Company.DoesNotExist as err:
            print(err)
            return Response(err)
        # except Exception as err:
        #     print(err)
        #     return Response({'status': False, 'message': err}, status=400)

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

    @classmethod
    def getTotalEmployees(self, companyId):
        try:
            users = User.objects.filter(companyId=companyId)
            serializer = UserSerializer(users, many=True)

            return len(serializer.data)
        except:
            pass

    @classmethod
    def getAdminName(self, companyId):
        try:
            admin = User.objects.get(companyId=companyId, userType='AD')
            serializer = UserSerializer(admin)

            return serializer.data['name']
        except:
            pass

    def get(self, request, companyId=None):
        try:
            if companyId is not None:
                company = Company.objects.get(companyId=companyId)
                serializer = CompanySerializer(company)

                companyData = {
                    'companyId': serializer.data['companyId'],
                    'name': serializer.data['name'],
                    'email': serializer.data['email'],
                    'image': serializer.data['image'],
                    'city': serializer.data['city'],
                    'country': serializer.data['country'],
                    'isApproved': serializer.data['isApproved'],
                    'noOfEmployees': self.getTotalEmployees(serializer.data['companyId']),
                    'adminName': self.getAdminName(serializer.data['companyId'])
                }

                return Response({'status': True, 'data': companyData})

            else:
                companies = Company.objects.all()
                serializer = CompanySerializer(companies, many=True)

                for company in serializer.data:
                    company['noOfEmployees'] = self.getTotalEmployees(
                        company['companyId'])
                    company['adminName'] = self.getAdminName(
                        company['companyId'])

                return Response({'status': True, 'data': serializer.data})

        except Company.DoesNotExist:
            return Response({'status': False, 'message': 'Company Does not exists'})
        # except Exception as err:
        #     return Response({'status': False, 'message': err})

    def post(self, request):
        # try:
        # companyData = request.data
        # company = Company(
        #     name=request.data['name'],
        #     email=request.data['email'],
        #     image=request.data['image'],
        #     city=request.data['city'],
        #     country=request.data['country'],
        # )

        company = {
            "companyId": ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7)),
            "name": request.data['name'],
            "email": request.data['email'],
            "image": request.data['image'],
            "city": request.data['city'],
            "country": request.data['country'],
        }
        compSerializer = CompanySerializer(data=company)
        if compSerializer.is_valid():
            compSerializer.save()
            print('Saved Company')
            return Response(compSerializer.data, status=201)
            # Creating Admin
            # admin = User(
            #     userId=request.data['adminId'],
            #     name=request.data['adminName'],
            #     email=request.data['adminEmail'],
            #     password=None,
            #     companyId=company,
            #     image=request.data['adminImage'],
            #     userType='NONE',
            #     designation=request.data['adminDesignation']
            # )

            # admin = {
            #     "userId": request.data['adminId'],
            #     "name": request.data['adminName'],
            #     "email": request.data['adminEmail'],
            #     "password": None,
            #     "companyId": company['companyId'],
            #     "image": request.data['adminImage'],
            #     "userType": 'NONE',
            #     "designation": request.data['adminDesignation']
            # }

            # empSerializer = UserSerializer(data=admin)
            # if empSerializer.is_valid():
            #     empSerializer.save()
            #     print('Saved Admin')
            #     return Response(compSerializer.data, status=201)
            # else:
            #     print(empSerializer.errors)
            #     return Response(empSerializer.errors)

        else:
            print('Company Not valid')
            return Response(compSerializer.errors)
        # except Exception as err:
        #     print(err)
        #     return Response({'status': False, 'message': err}, status=400)


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

    def post(self, request):
        try:
            data = request.data
            log = {
                "userId": User.objects.get(userId=data['userId']).userId,
                "companyId": Company.objects.get(companyId=data['companyId']).companyId,
                "type": data['type'],
                "datetime": data['datetime'],
                "location": data['location'],
            }
            serializer = LogSerializer(data=log)
            if serializer.is_valid():
                serializer.save()
                print("Saved Log: ")
                print(serializer.data)
                return Response({'status': True, 'data': serializer.data}, status=201)
            else:
                return Response(serializer.errors)
        except Company.DoesNotExist as err:
            print(err)
            return Response(err)
        except User.DoesNotExist as err:
            print(err)
            return Response(err)
        # except Exception as err:
        #     print(err)
        #     return Response({'status': False, 'message': err}, status=400)


class LoginApiView(APIView):
    def post(self, request):
        try:
            # Getting the user for the given email.
            data = request.data
            user = User.objects.get(email=data['email'])

            serializer = UserSerializer(user)
            if data['password'] == serializer.data['password']:
                if serializer.data['userType'] != 'NONE':
                    userData = serializer.data
                    refresh = RefreshToken.for_user(user)
                    refresh['userId'] = userData['userId']
                    refresh['userType'] = userData['userType']
                    token = refresh.access_token

                    responseData = {
                        'access': str(token),
                        'refresh': str(refresh),
                        'userId': userData['userId'],
                        'userId': userData['userId'],
                        'userType': userData['userType'],
                        'companyId': userData['companyId']
                    }

                    return Response({'status': True, 'data': responseData})
                else:
                    return Response({'status': False, 'message': 'Employee not active yet'})

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


class CompanyApprovalAPIView(APIView):

    def post(self, request):
        data = request.data

        if data['companyId'] or data['email'] or data['approve']:
            company = Company.objects.get(companyId=data['companyId'])

            if data['approve']:
                company.isApproved = True
                company.save()

                subject = 'Request Approved!!'
                message = '''
                <html>
                    <body>
                        <p>
                            Congratulations! Your Request is aprroved. Please find the login credentials below.
                        </p>
                        <h3>
                            <strong>Email: </strong>{email}
                            <strong>Email: </strong>{password}
                        </h3>
                    </body>
                </html>
                '''.format(email=data['email'], password='Random Pwd')
            else:
                company.delete()
                subject = 'Request Denied!'
                message = '''
                <html>
                    <body>
                        <p>
                            Your request to register your company was denied.
                        </p>
                    </body>
                </html>
                '''

                sendMail(data['email'], subject, message)

                return Response({'status': True, 'data': {
                    'result': 'Request Disapproved',
                    'message': 'Email sent successfuly'}
                })

        else:
            return Response({'status': False, 'message': 'Improper data received'})
