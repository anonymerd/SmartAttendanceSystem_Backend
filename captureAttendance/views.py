from captureAttendance.models import Employee, Image
from rest_framework import viewsets, permissions
from .serializers import ImageSerializer, EmployeeSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
import os
import re


from deepface import DeepFace
import pandas as pd


class ImageAPIView(APIView):

    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            # print(os.path.basename(serializer.data['image']))
            img = os.path.basename(serializer.data['image'])

            df = DeepFace.find(img_path='uploads/' + img, db_path="images/",
                               distance_metric='euclidean_l2',  enforce_detection=False)

            if df is None:
                print("No match found for given Person")
                return Response("No records found scan again", status=404)
            else:
                print("Match Found")
                sorted_df = df.sort_values(
                    by=['VGG-Face_euclidean_l2'], ascending=False)
                numoyArrOfDF = sorted_df.to_numpy()

                if numoyArrOfDF[0][1] < 0.65:
                    return Response("No records found scan again", status=404)
                else:

                    fileName = re.split("\/", numoyArrOfDF[0][0], 2)
                    empId = re.split("\.", fileName[2], 1)[0]

                    try:
                        recognizedEmp = Employee.objects.get(pk=empId)
                        empSerializer = EmployeeSerializer(recognizedEmp)
                        return Response(empSerializer.data, status=200)
                    except:
                        return Response("No records found scan again", status=404)

        try:
            os.remove("images/representations_vgg_face.pkl")
        except:
            print("No data to be removed")

        return Response(serializer.errors, status=400)


class EmployeeAPIView(APIView):

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request, format=None):
        names = [emp.empId for emp in Employee.objects.all()]
        return Response(names, status=200)
        # Employee.objects.all().delete()
        # return Response("Deleted", status=200)
