from django.urls import path
from django.conf.urls import url

from . import views

app_name= "main"
urlpatterns = [
    path('', views.Visits.as_view(), name="visits"),
    path('login', views.Login.as_view(), name='login'),  
    path('logout', views.Logout.as_view(), name='logout'),  
    path('remind_password', views.SendPassword.as_view(), name="remind_password"),
    path('add_security', views.AddSecurity.as_view(), name="add_security"),
    path('delete_security', views.DeleteSecurity.as_view(), name="delete_security"),
    path('delete_student', views.DeleteStudent.as_view(), name="delete_student"),
    path('stream', views.live_stream, name="stream"),
    path('student_stream', views.add_student_stream, name="student_stream"),
    path('show_stream', views.StreamView.as_view(), name="show_stream"),
    path('add_student', views.AddStudentStreamView.as_view(), name="add_student"),
    path('start_stop_stream', views.StartStopStream.as_view(), name="start_stop_stream"),
    path('start_student_stream', views.StartStudentStream.as_view(), name="start_student_stream"),
    path('download/(?P<path>.*)$', views.Download.as_view(), name="download"),

]