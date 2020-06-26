from ..models import Student, Security
from django.db.models import Q
from django.contrib.auth.models import User as MainAdmin

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_current_user(req):
    try:
        user = None
        user_id = req.session["user_id"]
        role = req.session["role"]
        if role == "admin":
            user = Security.objects.filter(id=user_id).first()
        elif role == "main_admin":
            user = MainAdmin.objects.filter(id=user_id).first()
        return user 
    except:
        return None  

def get_parameter(request, name):
    try:
        return request.GET[name]
    except:
        return None 

def post_parameter(request, name):
    try:
        return request.POST[name]
    except:
        return None 

def session_parameter(request, name):
    try:
        return request.session[name]
    except:
        return None

def filter_users(q):
    blocks = Student.objects.filter(Q(fullname__icontains=q) | Q(course__icontains=q) | Q(group__icontains=q))
    return blocks

def get_paginated_blogs(request, paginator):
    page = request.GET.get('page')
    try:
        page = int(page)
    except:
        page = 1
    a = ""
    block = ""
    pages=[]
    if page:
        try:
            block = paginator.page(page)
        except EmptyPage:
            block = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        for i in range(page-2, page+3):
            try:
                a = paginator.page(i)
                pages.append(i)
            except:
                continue
        print(pages)
        if pages[-1] != paginator.num_pages:
            pages.append(paginator.num_pages)

        if pages[0] != 1:
            pages.insert(0, 1)
    else:
        pages = [1,2,3,4,5,paginator.num_pages]
        block = paginator.page(1)
    return block, pages