from django.db.models import Count
from .models import Profile, Tag


def get_best_members(request):
    best_members = Profile.objects.annotate(
        activity=Count('questionlike', distinct=True) + Count('answerlike', distinct=True)
    ).order_by('-activity')[:5]
    return {'best_members': best_members}


def get_popular_tags(request):
    popular_tags = Tag.objects.annotate(
        num_questions=Count('question')
    ).order_by('-num_questions')[:8]
    return {'popular_tags': popular_tags}
