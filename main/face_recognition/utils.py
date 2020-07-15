import cv2
import numpy as np
import os
from django.contrib.staticfiles.storage import staticfiles_storage
from ..models import Security, Student, Visit, Face, BotUser
import pathlib
import datetime
from PIL import ImageFont, ImageDraw, Image
import pytz

uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])


class BotAction():
    bot = None


def getImagesAndLabels():
    faces=[] # Тут храним масив картинок
    ids = [] # Храним id лица
    for student in Student.objects.all():
        for face in student.images_urls.all():
            imagePath = uppath(str(pathlib.Path(__file__).parent.absolute()), 1) + face.img_url
            img = cv2.imread(imagePath)
            # Переводим изображение в серый, тренер понимает только одноканальное изображение
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces.append(img)
            ids.append(student.id)
    return faces,ids

def train():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces,ids = getImagesAndLabels()
    # Тренируем train(данные, id)
    recognizer.train(faces, np.array(ids))
    # Сохраняем результат
    recognizer_path = str(pathlib.Path(__file__).parent.absolute()) + "/face.yml"
    recognizer.write(recognizer_path)


def recognise_face(img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer_path = str(pathlib.Path(__file__).parent.absolute()) + "/face.yml"
    recognizer.read(recognizer_path)

    cascadePath = str(pathlib.Path(__file__).parent.absolute()) + "/haarcascade_frontalface_default.xml"
    #cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(10, 10),
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        student_id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        label = "unknown"
        # Проверяем что лицо распознано
        if (confidence > 40 and confidence < 100):
            b,g,r,a = 255,255,255,1
            student = Student.objects.filter(id=student_id).first()

            date_start = datetime.datetime.now()
            date_start = date_start.replace(hour=0, minute=0, second=0)

            date_end = datetime.datetime.now()
            date_end = date_start.replace(hour=23, minute=59, second=59)

            visits = Visit.objects.filter(visit_time__gte=date_start, visit_time__lte=date_end, student=student)
            if len(visits) == 0 and student:
                Visit.objects.create(student=student)

                if len(BotUser.objects.filter(student=student)) > 0:
                    if not BotAction.bot:
                        print("BOT STARTED")
                        BotAction.bot = Bot()

                    BotAction.bot.sendNotification(student)

            label = "unknown" if not student else student.fullname
            fontpath = "./simsun.ttc"
            font = ImageFont.truetype(fontpath, 12)
            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((x-40, y - 20),  label, font = font, fill = (b, g, r, a))
            img = np.array(img_pil)
            
            confidence = "  {0}%".format(round(100 - confidence))
        #cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
    ret, jpeg = cv2.imencode('.jpg', img)
    return jpeg.tobytes()

def recognise_face_without_title(img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cascadePath = str(pathlib.Path(__file__).parent.absolute()) + "/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(10, 10),
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    ret, jpeg = cv2.imencode('.jpg', img)
    return jpeg.tobytes()

def add_student(img, student, count):
    cascadePath = str(pathlib.Path(__file__).parent.absolute()) + "/haarcascade_frontalface_default.xml"
    face_detector = cv2.CascadeClassifier(cascadePath)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
    count_faces = 0
    if len(faces) > 1:
        ret, jpeg = cv2.imencode('.jpg', img)
        return False, jpeg.tobytes()

    for (x,y,w,h) in faces:     
        count_faces += 1
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)    
        # Сохраняем лицо
        path = uppath(str(pathlib.Path(__file__).parent.absolute()), 1) + '/static/faces/user.' + str(student.id) + '.' + str(count) + '.jpg' 
        static_path = staticfiles_storage.url('faces/user.' + str(student.id) + '.' + str(count) + '.jpg' )
        student.images_urls.add(Face.objects.create(img_url=static_path, absolute_path=path))
        print("path: " + path)
        cv2.imwrite(path, gray[y:y+h,x:x+w])

    ret, jpeg = cv2.imencode('.jpg', img)

    if count_faces > 0:
        return True, jpeg.tobytes()
    else:
        return False, jpeg.tobytes()
    

def create_blank(width, height, rgb_color=(0, 0, 0)):
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)
    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    ret, jpeg = cv2.imencode('.jpg', image)
    return jpeg.tobytes()

def delete_images(student):
    for face in student.images_urls.all():
        os.remove(face.absolute_path)
        face.delete()


def clear_face_uml():
    recognizer_path = str(pathlib.Path(__file__).parent.absolute()) + "/face.yml"
    file = open(recognizer_path, "w")
    file.truncate(0)
    file.close()