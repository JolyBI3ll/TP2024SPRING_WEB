from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import *
from .models import *
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import auth
from django.urls import reverse, resolve, Resolver404
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
import json
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout


# Create your views here.

def paginate(request, items, num_items=5):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(items, num_items)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def index(request):
    page_obj = paginate(request, Question.objects.get_new())
    return render(request, "index.html", {"questions": page_obj})


def hot(request):
    page_obj = paginate(request, Question.objects.get_hot())
    return render(request, "hot.html", {"questions": page_obj})


def question(request, question_id):
    item = Question.objects.get_one_question(question_id)
    if request.method == 'GET':
        answer_form = AnswerForm()
    if request.method == 'POST':
        if request.user.is_authenticated:
            answer_form = AnswerForm(data=request.POST, author=Profile.objects.get(user=request.user), question=item)
            if answer_form.is_valid():
                new_answer = answer_form.save()
                if new_answer:
                    answers = Answer.objects.all().filter(question=question_id)
                    pos = 0
                    for answer in answers:
                        pos += 1
                        if answer == new_answer:
                            break
                    return redirect(
                        reverse('question', kwargs={'question_id': question_id}) + '?page=' + str(pos // 5 + 1))
        else:
            return redirect(reverse('login'))
    page_obj = paginate(request, Answer.objects.get_by_question(question_id))
    return render(request, "question.html", {"question": item, "answers": page_obj, "form": answer_form})


def tag(request, tag):
    page_obj = paginate(request, Question.objects.get_by_tag(tag))
    return render(request, "tag.html", {"questions": page_obj, "tag": tag})


def member(request, name):
    member = Profile.objects.get_one_member(name)
    return render(request, "member.html", {"member": member})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    print(request.GET)
    redirect_page = request.GET.get('next', 'index')
    if request.method == 'GET':
        login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(reverse('index'))
            else:
                login_form.add_error(None, 'Wrong login or password')
                login_form.add_error('username', '')
                login_form.add_error('password', '')
    return render(request, "login.html", context={"form": login_form, "redirect_after": redirect_page})


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            nickname = form.cleaned_data.get('nickname')
            avatar = form.cleaned_data.get('avatar')

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken. Please choose another.')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already registered.')
            else:
                if not avatar:
                    avatar = 'avatar.png'
                user = form.save()
                Profile.objects.create(user=user, nickname=nickname, avatar=avatar)

                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, 'signup.html', {'form': form})


@login_required(login_url='login')
def logout(request):
    redirect_page = request.GET.get('next', 'index')

    try:
        resolve(redirect_page)
    except Resolver404:
        redirect_page = 'index'

    auth.logout(request)
    return redirect(redirect_page)


@login_required(login_url='login')
def ask(request):
    if request.method == 'GET':
        ask_form = AskForm()
    if request.method == 'POST':
        ask_form = AskForm(data=request.POST, author=Profile.objects.get(user=request.user))
        if ask_form.is_valid():
            question = ask_form.save()
            return redirect(reverse('question', kwargs={'question_id': question.id}))
    return render(request, "ask.html", {'form': ask_form})


@login_required(login_url='login')
def settings(request):
    if request.method == 'GET':
        settings_form = SettingsForm(user=request.user, avatar=Profile.objects.get(user=request.user).avatar)
    if request.method == 'POST':
        settings_form = SettingsForm(user=request.user, data=request.POST, files=request.FILES)
        if settings_form.is_valid():
            user = settings_form.save()
            if user:
                auth.login(request, user)
                return redirect(reverse('settings'))

    return render(request, "settings.html", {'form': settings_form, 'user': request.user})


@csrf_protect
@require_http_methods(['POST'])
def like_question(request):
    try:
        body = json.loads(request.body)
        question = get_object_or_404(Question, pk=body['questionId'])
        profile = get_object_or_404(Profile, user=request.user)
    except JSONDecodeError:
        return JsonResponse('Bad JSON', status=500)

    if body['isLike']:
        like_status = 1
    else:
        like_status = -1
    is_liked_already = QuestionLike.objects.filter(question=question, user=profile)
    if is_liked_already.exists():
        if int(is_liked_already.first().status) == like_status:
            question.rating -= like_status
            is_liked_already.first().delete()
        else:
            question.rating += like_status * 2
            is_liked_already.first().delete()
            QuestionLike.objects.create(question=question, user=profile, status=like_status)
    else:
        question.rating += like_status
        QuestionLike.objects.create(question=question, user=profile, status=like_status)

    question.save()
    return JsonResponse({
        'rating': question.rating
    })


@csrf_protect
@require_http_methods(['POST'])
def like_answer(request):
    try:
        body = json.loads(request.body)
        answer = get_object_or_404(Answer, pk=body['answerId'])
        profile = get_object_or_404(Profile, user=request.user)
    except JSONDecodeError:
        return JsonResponse('Bad JSON', status=500)

    if body['isLike']:
        like_status = 1
    else:
        like_status = -1
    is_liked_already = AnswerLike.objects.filter(answer=answer, user=profile)
    print(like_status)
    if is_liked_already.exists():
        if int(is_liked_already.first().status) == like_status:
            answer.rating -= like_status
            is_liked_already.first().delete()
        else:
            answer.rating += like_status * 2
            is_liked_already.first().delete()
            AnswerLike.objects.create(answer=answer, user=profile, status=like_status)
    else:
        answer.rating += like_status
        AnswerLike.objects.create(answer=answer, user=profile, status=like_status)

    answer.save()
    return JsonResponse({
        'rating': answer.rating
    })


@csrf_protect
@require_http_methods(["POST"])
def mark_answer(request):
    try:
        body = json.loads(request.body)
        answer = get_object_or_404(Answer, pk=body['answerId'])
        question = get_object_or_404(Question, pk=body['questionId'])
        is_correct = body['isCorrect']
    except KeyError or JSONDecodeError:
        return JsonResponse('Bad JSON', status=500)

    if question.author.id != request.user.profile.id:
        return HttpResponseBadRequest('Only author of the question is able to mark answer as correct')

    if is_correct:
        answer.status = 'm'
    else:
        answer.status = 'mn'
    answer.save()
    return JsonResponse('Marked', status=200, safe=False)
