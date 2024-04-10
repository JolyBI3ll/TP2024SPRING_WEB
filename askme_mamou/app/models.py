from django.db import models
from django.contrib.auth.models import User
from django.http import Http404


# Model Manager для вопросов
class QuestionManager(models.Manager):
    def get_hot(self):
        return self.all().order_by('-rating')

    def get_new(self):
        return self.all().order_by('created_at')

    def get_by_tag(self, tag_name):
        try:
            return self.filter(tags__name=tag_name)
        except Question.DoesNotExist:
            return Http404("Question not found!")

    def get_one_question(self, question_id):
        try:
            return self.all().get(id=question_id)
        except Question.DoesNotExist:
            return Http404("Question not found!")


class AnswerManager(models.Manager):
    def get_by_question(self, question_id):
        try:
            return self.all().filter(question__id=question_id).order_by('status')
        except Question.DoesNotExist:
            return Http404("Question does not exist")


class ProfileManager(models.Manager):
    def get_one_member(self, member_name):
        try:
            return self.get(nickname=member_name)
        except Profile.DoesNotExist:
            raise Http404("Profile is not found!")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='uploads/', default='img/avatar.png', null=True, blank=True)
    nickname = models.CharField(max_length=255, blank=True)
    activity = models.IntegerField(default=0)
    likes_count_answer = models.IntegerField(default=0)
    likes_count_question = models.IntegerField(default=0)

    objects = ProfileManager()

    def __str__(self):
        return self.nickname


class Tag(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_questions = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Question(models.Model):
    STATUS_CHOICES = (('S', 'Solved'), ('N', 'Not Solved'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)
    num_answers = models.IntegerField(default=0)

    objects = QuestionManager()  # Использование собственного менеджера моделей

    def __str__(self):
        return self.title


class Answer(models.Model):
    STATUS_CHOICES = [('m', 'Marked as right'), ('nm', 'Not marked')]
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='nm')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)

    objects = AnswerManager()

    def __str__(self):
        return self.text  # Возвращает начало текста ответа


# Модель для лайков вопросов
class QuestionLike(models.Model):
    STATUS_CHOICES = [("l", "Like"), ("d", "Dislike"), ("n", "Not liked")]
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='d')

    class Meta:
        unique_together = ('user', 'question')  # Ограничение на уникальность пары пользователь-вопрос

    def __str__(self):
        return f'{self.user.nickname} likes {self.question.title}'


# Модель для лайков ответов
class AnswerLike(models.Model):
    STATUS_CHOICES = [("l", "Like"), ("d", "Dislike"), ("n", "Not liked")]
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='d')

    class Meta:
        unique_together = ('user', 'answer')  # Ограничение на уникальность пары пользователь-ответ

    def __str__(self):
        return f'{self.user.nickname} likes answer {self.answer.id}'
