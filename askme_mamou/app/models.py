from django.db import models
from django.contrib.auth.models import User


# Model Manager для вопросов
class QuestionManager(models.Manager):
    def get_hot(self):
        # Пример реализации, например, выборка по количеству лайков
        return self.annotate(likes_count=models.Count('questionlike')).order_by('-likes_count')

    def get_new(self):
        # Пример реализации, выборка по дате создания
        return self.order_by('created_at').annotate(likes_count=models.Count('questionlike'))

    def get_tag(self, tag_name):
        return self.filter(tags__name=tag_name).annotate(likes_count=models.Count('questionlike'))


class TagManager(models.Manager):
    def get_popular(self):
        return self.all().order_by('created_at')


class AnswerManager(models.Manager):
    def get_by_question(self, question_id):
        return self.filter(question__id=question_id).order_by('status').annotate(likes_count=models.Count('answerlike'))


class ProfileManager(models.Manager):
    def get_best_members(self):
        pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    nickname = models.CharField(max_length=255, blank=True)
    rating = models.IntegerField()
    objects = ProfileManager()

    def __str__(self):
        return self.nickname


class Tag(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TagManager()

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')  # Ограничение на уникальность пары пользователь-вопрос

    def __str__(self):
        return f'{self.user.username} likes {self.question.title}'


# Модель для лайков ответов
class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')  # Ограничение на уникальность пары пользователь-ответ

    def __str__(self):
        return f'{self.user.username} likes answer {self.answer.id}'
