import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from ...models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike


class Command(BaseCommand):
    help = 'Fills the database with test data based on the given ratio.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='The fill ratio for test data')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        fake = Faker()

        django_users = [User(username=fake.unique.user_name(), email=fake.unique.email(), password=fake.password())
                        for i in range(ratio)]
        User.objects.bulk_create(django_users, batch_size=10000)

        # Создаем профили пользователей
        user_profiles = [Profile(user=user, nickname=fake.unique.user_name(), avatar=None)
                         for i, user in enumerate(django_users)]
        Profile.objects.bulk_create(user_profiles, batch_size=10000)

        profiles = list(Profile.objects.all())

        # Создание тэгов
        tags = [Tag(name=f"Tag {i}") for i in range(ratio)]
        Tag.objects.bulk_create(tags, batch_size=10000)
        tag_list = list(Tag.objects.all())

        # Создание вопросов
        questions = [Question(title=fake.sentence(), text=fake.text(), author=random.choice(profiles)) for _ in
                     range(ratio * 10)]
        Question.objects.bulk_create(questions, batch_size=10000)
        for question in Question.objects.all():
            question.tags.add(*random.sample(tag_list, min(len(tag_list), random.randint(1, 3))))

        # Создание ответов
        QUESTIONS_CHOICES = list(Question.objects.all())

        answers = []
        for i in range(ratio * 100):
            answers.append(Answer(text=fake.text(),
                                  author=random.choice(profiles),
                                  question=random.choice(QUESTIONS_CHOICES)))
        Answer.objects.bulk_create(answers, batch_size=10000)

        # Создание лайков вопросов
        LIKE_STATUS_CHOICE = ['l', 'd']
        QUESTION_LIKE = []
        used_pairs = set()
        i = 0
        while i != (ratio * 100):
            user = random.choice(profiles)
            question = random.choice(QUESTIONS_CHOICES)
            pair = (user, question)
            if pair not in used_pairs:
                QUESTION_LIKE.append(QuestionLike(user=user,
                                                  question=question,
                                                  status=random.choice(LIKE_STATUS_CHOICE)))
                used_pairs.add(pair)
                i += 1
        QuestionLike.objects.bulk_create(QUESTION_LIKE, batch_size=10000)

        # Создание лайков ответов
        ANSWERS_CHOICES = list(Answer.objects.all())
        ANSWER_LIKE = []
        used_pairs.clear()
        i = 0
        while i != (ratio * 100):
            user = random.choice(profiles)
            answer = random.choice(ANSWERS_CHOICES)
            pair = (user, answer)
            if pair not in used_pairs:
                ANSWER_LIKE.append(AnswerLike(user=user,
                                              answer=answer,
                                              status=random.choice(LIKE_STATUS_CHOICE)))
                used_pairs.add(pair)
                i += 1
        AnswerLike.objects.bulk_create(ANSWER_LIKE, batch_size=10000)

        # Вычисление num_questions в модели tag
        tags_to_update = []
        for tag in Tag.objects.all():
            tag.num_questions = tag.question_set.count()
            tags_to_update.append(tag)
        Tag.objects.bulk_update(tags_to_update, ['num_questions'], batch_size=10000)

        # Вычисление поля num_answers и rating в модели Question
        questions_to_update = []
        for question in Question.objects.all():
            question.num_answers = question.answer_set.count()
            questionlikes = QuestionLike.objects.filter(question=question)
            question.rating = questionlikes.filter(status='l').count() - questionlikes.filter(status='d').count()
            questions_to_update.append(question)
        Question.objects.bulk_update(questions_to_update, ['num_answers', 'rating'], batch_size=10000)

        # Вычисление полей likes_count_answer и likes_count_question и activity в модели Profile
        profiles_to_update = []
        for profile in Profile.objects.all():
            profile.likes_count_question = profile.questionlike_set.count()
            profile.likes_count_answer = profile.answerlike_set.count()
            profile.activity = profile.likes_count_question + profile.likes_count_answer
            profiles_to_update.append(profile)
        Profile.objects.bulk_update(profiles_to_update, ['likes_count_answer', 'likes_count_question', 'activity'], batch_size=10000)

        # Вычисление полей rating в модели Answer
        answers_to_update = []
        for answer in Answer.objects.all():
            answerlikes = AnswerLike.objects.filter(answer=answer)
            answer.rating = answerlikes.filter(status='l').count() - answerlikes.filter(status='d').count()
            answers_to_update.append(answer)
        Answer.objects.bulk_update(answers_to_update, ['rating'], batch_size=10000)

        self.stdout.write(self.style.SUCCESS(f'Successfully added test data with ratio {ratio}.'))
