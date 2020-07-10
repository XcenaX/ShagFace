from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import Security, Student, Visit, Face
import os
import io
from imageio import imread

import base64

from django.db.models import Q

from django.contrib.auth.models import User as MainAdmin

from django.http import HttpResponse, Http404

from .modules.hashutils import check_pw_hash, make_pw_hash
from .modules.sendEmail import *

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .modules.utils import *
from .modules.TimedValue import TimedValue

from django.contrib.auth.hashers import check_password

from .Classes.Camera import Camera
from .Classes.Bot import Bot
from django.http import StreamingHttpResponse
import cv2
import numpy as np

from django.views.decorators.gzip import gzip_page

from django.template import loader, Context

from .face_recognition.utils import *

from django.http import JsonResponse

COUNT_BLOG_ON_PAGE = 50
STUDENT_PHOTOS = 5
TIME_TO_WAIT = 3 # Время которое пройдет после того как камера распознает студента чтобы показать следующую картинку
CURRENT_STUDENT_TO_ADD = None

class CameraAction():
    current_student = None

class Logout(View):
    def post(self, request):
        try:
            del request.session["user_id"]
        except:
            print("error")
        return redirect(reverse('main:login'))

class Download(View):
    def post(self, request, path):
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404

class SendPassword(View):
    def get(self, request):
        return render(request, 'remind_password.html', {})

    def post(self, request):
        email = post_parameter(request, "email")
        if email:
            admin = MainAdmin.objects.filter(email=email).first()
            if admin:
                send_email(admin.password, "Ваш пароль", admin.email)
            else:
                return render(request, 'remind_password.html', {
                    "login_error" : "Пользователяс таким Email не найдено!",
                })
        return redirect(reverse("main:login"))


class Login(View):
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        email_or_username = post_parameter(request, "username")
        password = post_parameter(request, "pass")
        user = None
        role = "admin"

        login_valid = (settings.ADMIN_LOGIN == email_or_username or settings.ADMIN_EMAIL == email_or_username)
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)

        if login_valid and pwd_valid:
            user = MainAdmin.objects.filter(Q(username=email_or_username) | Q(email=email_or_username)).first()
            role = "main_admin"
            request.session["user_id"] = user.id
            request.session["role"] = role
            return redirect(reverse('main:visits'))
            
        
        user = Security.objects.filter(email=email_or_username).first()
        if not user:
            user = Security.objects.filter(login=email_or_username).first()  

        if user:
            if check_pw_hash(password, user.password):
                request.session["user_id"] = user.id
                request.session["role"] = role
                return redirect(reverse('main:visits'))
            else:
                return render(request, 'login.html', {
                    "login_error" : "Неверный логин или пароль!",
                })
        else:
            return render(request, 'login.html', {
                "login_error" : "Неверный логин или пароль!",
            })
            
class AddSecurity(View):
    def get(self, request):
        if not get_current_user(request):
            return redirect(reverse('main:login'))
        return render(request, 'add_security.html', {
            "user": get_current_user(request),  
            "nomargin": True,
        })
    
    def post(self, request):
        email = post_parameter(request, "email")
        login = post_parameter(request, "login")
        password = post_parameter(request, "pass")
        fullname = post_parameter(request, "fullname")

        hash_password = make_pw_hash(password)

        if len(Security.objects.filter(Q(email=email) | Q(login=login))) > 0:
            return render(request, 'add_security.html', {
                "add_error" : "Такой пользователь уже сущетсвует!",
            })
        Security.objects.create(email=email, login=login, password=hash_password, fullname=fullname)
        return render(request, 'add_security.html', {
            "success" : "Вы успешно добавили охранника!",
        })


class DeleteSecurity(View):
    def get(self, request):
        if not get_current_user(request):
            return redirect(reverse('main:login'))
        securities = Security.objects.all()
        return render(request, 'delete_security.html', {
            "user": get_current_user(request),  
            "securities": securities
        })
    
    def post(self, request):
        security_id = post_parameter(request, "id")
        security =Security.objects.filter(id=security_id).first()
        if not security:
            return render(request, 'delete_security.html', {
                "delete_error" : "Не удалось найти пользователя для удаления!",
            })
        security.delete()
        return render(request, 'delete_security.html', {
            "success" : "Вы успешно удалили охранника!",
            "securities": Security.objects.all()
        })

class DeleteStudent(View):
    def get(self, request):
        if not get_current_user(request):
            return redirect(reverse('main:login'))

        students = Student.objects.all()
        return render(request, 'delete_student.html', {
            "user": get_current_user(request),  
            "students": students
        })
    
    def post(self, request):
        student_id = post_parameter(request, "id")
        student = Student.objects.filter(id=student_id).first()
        if not student:
            return render(request, 'delete_student.html', {
                "delete_error" : "Не удалось найти пользователя для удаления!",
            })
        delete_images(student)
        student.delete()
        return render(request, 'delete_student.html', {
            "success" : "Вы успешно удалили студента!",
            "students": Student.objects.all()
        })

class Visits(View):
    if not BotAction.bot:
        print("BOT STARTED")
        BotAction.bot = Bot()
        
    def get(self, request):
        if not get_current_user(request):
            return redirect(reverse('main:login'))

        return render(request, 'visits.html', {
            "user": get_current_user(request),  
            "nomargin": True,
            "visits": Visit.objects.all()
        })

class SetCurrentStudentToAdd(View):
    def post(self, request):
        student_id = int(post_parameter(request, "student_id"))
        CameraAction.current_student = Student.objects.filter(id=student_id).first()
        return JsonResponse({"success": "ok"})  

class Train(View):
    def post(self, request):
        train()
        return JsonResponse({"success": "ok"})

class AddStudentStreamView(View):
    def get(self, request):
        return render(request, 'add_student.html', {
            "user" : get_current_user(request),
            "nomargin": True,
            "TIME_TO_WAIT": TIME_TO_WAIT,
        })
    def post(self, request):
        str_img = post_parameter(request, "image")
        count = int(post_parameter(request, "count"))

        img = from_base64(str_img.split(",")[1])
        is_added, img = add_student(img, CameraAction.current_student, count)

        return JsonResponse({"image": str(img), "is_added": str(is_added)})  

class StreamView(View):
    def get(self, request):
        return render(request, 'stream.html', {
            "user" : get_current_user(request),
            "nomargin": True,
        })



class RecognizeFace(View):
    def post(self, request):
        str_img = post_parameter(request, "image")
        #img = stringToImage(str_img.split(",")[1])
        #recognized_image = recognise_face(np.array(img))
        img = from_base64(str_img.split(",")[1])
        recognized_image = recognise_face(img)
        
        
        return JsonResponse({"image": str(recognized_image)})


class StartStudentStream(View):
    def post(self, request):
        email = post_parameter(request, "email")
        fullname = post_parameter(request, "fullname")
        group = post_parameter(request, "group")
        course = post_parameter(request, "course")

        if len(Student.objects.filter(email=email)) > 0:
            return JsonResponse({"error": "Такой пользователь уже существует!"})        
        
        student  = Student.objects.create(email=email, fullname=fullname, group=group, course=course)

        return JsonResponse({"success": "true", "student_id": student.id})
