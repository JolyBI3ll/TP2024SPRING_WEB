from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Case, When, IntegerField
from django.shortcuts import get_object_or_404


def likes_count_question(model):
    qs_with_like_count = model.objects.annotate(
        like_count=Sum(
            Case(
                When(questionlike__status='l', then=1),
                When(questionlike__status='d', then=-1),
                default=0,
                output_field=IntegerField()
            )
        )
    )
    return qs_with_like_count


def likes_count_answer(model):
    qs_with_like_count = model.objects.annotate(
        like_count=Sum(
            Case(
                When(answerlike__status='l', then=1),
                When(answerlike__status='d', then=-1),
                default=0,
                output_field=IntegerField()
            )
        )
    )
    return qs_with_like_count


# Model Manager для вопросов
class QuestionManager(models.Manager):
    def get_hot(self):
        hot_questions = likes_count_question(Question).order_by('-like_count')
        return hot_questions

    def get_new(self):
        new_questions = likes_count_question(Question).order_by('created_at')
        return new_questions

    def get_by_tag(self, tag_name):
        try:
            question_tags = likes_count_question(Question).filter(tags__name=tag_name)
        except Tag.DoesNotExist:
            get_object_or_404(Tag, tags__name=tag_name)
        return question_tags

    def get_one_question(self, question_id):
        try:
            question = likes_count_question(Question).get(id=question_id)
        except Question.DoesNotExist:
            get_object_or_404(Question, id=question_id)
        return question


class AnswerManager(models.Manager):
    def get_by_question(self, question_id):
        try:
            answers = likes_count_answer(Answer).filter(question__id=question_id).order_by('status')
        except Answer.DoesNotExist:
            get_object_or_404(Answer, question__id=question_id)
        return answers


class ProfileManager(models.Manager):
    def get_one_member(self, member_name):
        try:
            profile = self.annotate(likes_count_question=models.Count('questionlike', distinct=True)).annotate(
                likes_count_answer=models.Count('answerlike', distinct=True)).get(nickname=member_name)
        except Profile.DoesNotExist:
            return get_object_or_404(Profile, nickname=member_name)

        return profile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    nickname = models.CharField(max_length=255, blank=True)

    objects = ProfileManager()

    def __str__(self):
        return self.nickname


class Tag(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    objects = AnswerManager()

    def __str__(self):
        return self.text  # Возвращает начало текста ответа


# Модель для лайков вопросов
class QuestionLike(models.Model):
    STATUS_CHOICES = [("l", "Like"), ("d", "Dislike")]
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
    STATUS_CHOICES = [("l", "Like"), ("d", "Dislike")]
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='d')

    class Meta:
        unique_together = ('user', 'answer')  # Ограничение на уникальность пары пользователь-ответ

    def __str__(self):
        return f'{self.user.nickname} likes answer {self.answer.id}'
