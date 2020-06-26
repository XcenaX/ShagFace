from django.db import models
from django.utils import timezone
from django.conf import settings

class Face(models.Model):
    img_url = models.TextField(blank=True)
    absolute_path = models.TextField(blank=True)

class Student(models.Model):
    email = models.TextField(default="") 
    fullname= models.TextField(default="") 
    images_urls = models.ManyToManyField(Face, related_name='faces',  blank=True)
    parent_number = models.TextField(default="")
    parent_telegram = models.TextField(default="")
    group = models.TextField(default="")
    course = models.TextField(default="")
    def __str__(self):
        return self.fullname

class Security(models.Model):
    email = models.TextField(default="") 
    password = models.TextField(default="") 
    login = models.TextField(default="") 
    fullname= models.TextField(default="") 
    def __str__(self):
        return self.fullname

class Visit(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    visit_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.student.fullname

class BotUser(models.Model):
    chat_id = models.IntegerField(null=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.chat_id)