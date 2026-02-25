from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    # Главные страницы
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('start-learning/', views.start_learning, name='start_learning'),
    path('post/<slug:post_slug>/', views.post_detail, name='post'),
    
    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Курсы
    path('neuro-start/', views.neuro_start, name='neuro_start'),
    path('prompteng-start/', views.prompteng_start, name='prompteng_start'),
    
    # Уроки внутри курса нейросетей (все с префиксом neuro-start/)
    path('neuro-start/lesson/<int:lesson_id>/', views.neuro_lesson_detail, name='neuro_lesson_detail'),
    path('neuro-start/test/<int:test_id>/', views.neuro_test_detail, name='neuro_test_detail'),
    path('neuro-start/check-answer/', views.neuro_check_answer, name='neuro_check_answer'),
    path('neuro-start/mark-complete/<int:lesson_id>/', views.neuro_mark_complete, name='neuro_mark_complete'),
    path('neuro-start/progress/', views.neuro_progress, name='neuro_progress'),
    path('neuro-start/results/', views.neuro_results, name='neuro_results'),

     # Курс Ethernet
    path('ethernet-start/', views.ethernet_start, name='ethernet_start'),
    path('ethernet-start/lesson/<int:lesson_id>/', views.ethernet_lesson_detail, name='ethernet_lesson_detail'),
    path('ethernet-start/test/<int:test_id>/', views.ethernet_test_detail, name='ethernet_test_detail'),
    path('ethernet-start/check-answer/', views.ethernet_check_answer, name='ethernet_check_answer'),
    path('ethernet-start/mark-complete/<int:lesson_id>/', views.ethernet_mark_complete, name='ethernet_mark_complete'),

    # Курс Prompt Engineering
    path('prompteng-start/', views.prompteng_start, name='prompteng_start'),
    path('prompteng-start/lesson/<int:lesson_id>/', views.prompteng_lesson_detail, name='prompteng_lesson_detail'),
    path('prompteng-start/test/<int:test_id>/', views.prompteng_test_detail, name='prompteng_test_detail'),
    path('prompteng-start/check-answer/', views.prompteng_check_answer, name='prompteng_check_answer'),
    path('prompteng-start/mark-complete/<int:lesson_id>/', views.prompteng_mark_complete, name='prompteng_mark_complete'),
]