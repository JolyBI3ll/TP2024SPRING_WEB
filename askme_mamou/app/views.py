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
    question = Question.objects.get(pk=question_id)
    answers = Answer.objects.get_by_question(question_id)
    ans_obj = paginate(request, answers)
    return render(request, "question.html", {"question": question, "answers": ans_obj})


def tag(request, tag):
    page_obj = paginate(request, Question.objects.get_tag(tag))
    return render(request, "tag.html", {"questions": page_obj, "tag": tag})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def ask(request):
    return render(request, "ask.html")


def settings(request):
    user = Profile.objects.get(user__is_active=True)
    return render(request, "settings.html", {"user": user})


def member(request, name):
    member = Profile.objects.get(user__username=name)
    return render(request, "member.html", {"member": member})
