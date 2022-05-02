import face_recognition
import os
from django.conf import settings
from scipy.misc import face


def recognize():
    # print(os.listdir(os.path.join(settings.MEDIA_ROOT, 'images/user')))

    for image in os.listdir('images/user'):
        print(image)

        known_image = face_recognition.load_image_file('images/user/' + image)
        unknown_image = face_recognition.load_image_file(
            'uploads/rohit.jpg')

        known_encoding = face_recognition.face_encodings(known_image)
        unknown_encoding = face_recognition.face_encodings(unknown_image)

        if(len(known_encoding) > 0 and len(unknown_encoding) > 0):

            results = face_recognition.compare_faces(
                [known_encoding[0]], unknown_encoding[0])
            print(results)
