from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('questions/<int:question_id>', views.question, name='question'),
    path('hot/', views.hot, name='hot'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tag>', views.tag, name='tag'),
    path('profile/edit/', views.settings, name='settings'),
    path('member/<str:name>', views.member, name='member'),
    path('logout/', views.logout, name = 'logout'),
]
