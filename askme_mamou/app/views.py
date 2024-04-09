from django.shortcuts import render
from django.core.paginator import Paginator
from .models import *


# Create your views here.

def paginate(request, items, num_items=5):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(items, num_items)
    page_obj = paginator.page(page_num)
    return page_obj


def index(request):
    page_obj = paginate(request, Question.objects.get_new())
    return render(request, "index.html", {"questions": page_obj})


def hot(request):
    page_obj = paginate(request, Question.objects.get_hot())
    return render(request, "hot.html", {"questions": page_obj})


def question(request, question_id):
    question = Question.objects.get_one_question(question_id)
    ans_obj = paginate(request, Answer.objects.get_by_question(question_id))
    return render(request, "question.html", {"question": question, "answers": ans_obj})


def tag(request, tag):
    page_obj = paginate(request, Question.objects.get_by_tag(tag))
    return render(request, "tag.html", {"questions": page_obj, "tag": tag})


def member(request, name):
    member = Profile.objects.get_one_member(name)
    return render(request, "member.html", {"member": member})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def ask(request):
    return render(request, "ask.html")


def settings(request):
    user = Profile.objects.get(user__is_active=True)
    return render(request, "settings.html", {"user": user})
