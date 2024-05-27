from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('questions/<int:question_id>', views.question, name='question'),
    path('hot/', views.hot, name='hot'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tag>', views.tag, name='tag'),
    path('profile/edit/', views.settings, name='settings'),
    path('member/<str:name>', views.member, name='member'),
    path('logout/', views.logout, name='logout'),
    path('like-question/', views.like_question, name='like-question'),
    path('like-answer/', views.like_answer, name='like-answer'),
    path('mark-answer/', views.mark_answer, name='mark-answer')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
