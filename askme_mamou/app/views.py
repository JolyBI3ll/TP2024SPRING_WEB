from django.shortcuts import render
from django.core.paginator import Paginator

# Create your views here.

TAGS = [
    "Python",
    "Mail.ru",
    "Yandex",
    "Perl",
    "Rust",
    "MySQL",
    "Django",
    "Firefox"
]

QUESTIONS = [
    {
        "id": i,
        "title": f"Question {i}",
        "text": f"This is question number {i}",
        "tags": [TAGS[i % 8], TAGS[(i - 2) % 8]],
    } for i in range(200)
]

ANSWERS = [
    {
        "id": i,
        "text": f"Dear, {i}! The question you asked is very intriguing and multifaceted. To comprehensively answer "
                f"it, it is necessary to consider many factors and points of view. However, given the complexity of "
                f"the question, I'm not sure I can provide an exhaustive answer that will satisfy everyone.",
        "question_id": i % 100
    } for i in range(1000)
]

MEMBERS = [
    {
        "id": i,
        "name": f"member {i}",
        "email": f"mail{i}@mail.ru",
    } for i in range(100)
]


def paginate(request, items, num_items=5):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(items, num_items)
    page_obj = paginator.page(page_num)
    return page_obj


def index(request):
    page_obj = paginate(request, QUESTIONS)
    return render(request, "index.html", {"questions": page_obj})


def hot(request):
    questions = QUESTIONS[::-1]
    page_obj = paginate(request, questions)
    return render(request, "hot.html", {"questions": page_obj})


def question(request, question_id):
    question = QUESTIONS[question_id]
    answers = [answer for answer in ANSWERS if answer["question_id"] == question_id]
    ans_obj = paginate(request, answers)
    return render(request, "question.html", {"question": question, "answers": ans_obj})


def tag(request, tag):
    questions = [q for q in QUESTIONS if tag in q['tags']]
    page_obj = paginate(request, questions)
    return render(request, "tag.html", {"questions": page_obj, "tag": tag})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def ask(request):
    return render(request, "ask.html")


def settings(request):
    return render(request, "settings.html")


def member(request, name):
    for member in MEMBERS:
        if member["name"] == name:
            return render(request, "member.html", {"member": member})

    return render(request, "member.html", {"member": {"name": "default_name", "email": "default_email"}})
