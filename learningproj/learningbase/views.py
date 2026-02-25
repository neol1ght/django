from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .form import RegisterForm, LoginForm

from .models import Post, TestAnswer, UserProgress, Lesson

# Create your views here.


def home(request):
    posts = Post.objects.all()
    data = {
        "title": "Главная",
        "posts": posts,
    }
    return render(request, 'learningbase/index.html', context=data)

def about(request):
    data = {
        "title": "О нас",
    }
    return render(request, 'learningbase/about.html', context=data)

def start_learning(request):
    data = {
        "title": "Начать обучение",
    }
    return render(request, 'learningbase/start_learning.html', context=data)

def post_detail(request, post_slug):
    """Детальная страница поста"""
    post = get_object_or_404(Post, slug=post_slug)
    
    context = {
        'title': post.name,
        'post': post,
    }
    
    return render(request, 'learningbase/post_detail.html', context)

@login_required
def neuro_start(request):
    """Главная страница курса нейросети"""
    # Получаем или создаем сессию пользователя
    if not request.session.session_key:
        request.session.save()
    
    # Получаем все уроки курса нейросети
    lessons = Lesson.objects.filter(course='neuro').prefetch_related('questions__answers').order_by('order')
    
    # Отдельно получаем статьи и тесты для нумерации
    articles = Lesson.objects.filter(course='neuro', lesson_type='article').order_by('order')
    tests = Lesson.objects.filter(course='neuro', lesson_type='test').order_by('order')
    
    # Создаем словари для хранения номеров
    article_numbers = {}
    test_numbers = {}
    
    for i, article in enumerate(articles, 1):
        article_numbers[article.id] = i
    
    for i, test in enumerate(tests, 1):
        test_numbers[test.id] = i
    
    # Получаем прогресс пользователя
    completed_lessons = UserProgress.objects.filter(
        session_key=request.session.session_key,
        completed=True,
        lesson__course='neuro'
    ).values_list('lesson_id', flat=True)
    
    for lesson in lessons:
        lesson.completed = lesson.id in completed_lessons
        # Добавляем номер в зависимости от типа
        if lesson.lesson_type == 'article':
            lesson.display_number = article_numbers.get(lesson.id, '?')
            lesson.display_type = 'Статья'
        else:
            lesson.display_number = test_numbers.get(lesson.id, '?')
            lesson.display_type = 'Тест'
    
    context = {
        'title': 'Нейросети для начинающих',
        'lessons': lessons,
        'completed_count': len(completed_lessons),
        'total_lessons': lessons.count(),
        'articles_count': articles.count(),
        'tests_count': tests.count(),
    }
    
    return render(request, 'learningbase/neuro_start.html', context)

@login_required
def neuro_lesson_detail(request, lesson_id):
    """Детальная страница урока (статья) для Neuro"""
    if not request.session.session_key:
        request.session.save()
    
    lesson = get_object_or_404(Lesson, id=lesson_id, course='neuro', lesson_type='article')
    
    # Проверяем, завершен ли урок
    is_completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        lesson=lesson,
        completed=True
    ).exists()
    
    # Получаем все уроки для навигации
    all_lessons = list(Lesson.objects.filter(course='neuro').order_by('order'))
    current_index = None
    
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
            break
    
    # Получаем все статьи для нумерации
    all_articles = Lesson.objects.filter(course='neuro', lesson_type='article').order_by('order')
    article_numbers = {}
    for i, article in enumerate(all_articles, 1):
        article_numbers[article.id] = i
    
    prev_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    context = {
        'title': lesson.title,
        'lesson': lesson,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'all_lessons': all_lessons,
        'current_index': current_index + 1,
        'total_lessons': len(all_lessons),
        'current_article_number': article_numbers.get(lesson.id, 1),
        'total_articles': all_articles.count(),
    }
    
    return render(request, 'learningbase/neuro_lesson.html', context)

@login_required
def neuro_test_detail(request, test_id):
    """Страница с тестом для Neuro"""
    if not request.session.session_key:
        request.session.save()
    
    lesson = get_object_or_404(Lesson, id=test_id, course='neuro', lesson_type='test')
    questions = lesson.questions.prefetch_related('answers').all()
    
    # Проверяем, завершен ли тест
    is_completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        lesson=lesson,
        completed=True
    ).exists()
    
    # Получаем все уроки для навигации
    all_lessons = list(Lesson.objects.filter(course='neuro').order_by('order'))
    current_index = None
    
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
            break
    
    # Получаем все тесты для нумерации
    all_tests = Lesson.objects.filter(course='neuro', lesson_type='test').order_by('order')
    test_numbers = {}
    for i, test in enumerate(all_tests, 1):
        test_numbers[test.id] = i
    
    prev_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    context = {
        'title': lesson.title,
        'lesson': lesson,
        'questions': questions,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'current_index': current_index + 1,
        'total_lessons': len(all_lessons),
        'current_test_number': test_numbers.get(lesson.id, 1),
        'total_tests': all_tests.count(),
    }
    
    return render(request, 'learningbase/neuro_test.html', context)

@login_required
def neuro_check_answer(request):
    """Проверка ответа на вопрос для Neuro (AJAX)"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        try:
            answer = TestAnswer.objects.get(id=answer_id, question_id=question_id)
            
            if answer.is_correct:
                return JsonResponse({
                    'correct': True,
                    'message': 'Правильно!',
                    'question_id': question_id
                })
            else:
                return JsonResponse({
                    'correct': False,
                    'message': 'Неправильно. Попробуй еще!'
                })
                
        except TestAnswer.DoesNotExist:
            return JsonResponse({'error': 'Ответ не найден'}, status=404)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def neuro_mark_complete(request, lesson_id):
    """Отметить урок Neuro как пройденный"""
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.save()
        
        lesson = get_object_or_404(Lesson, id=lesson_id, course='neuro')
        
        # Создаем или обновляем запись о прогрессе
        progress, created = UserProgress.objects.get_or_create(
            session_key=request.session.session_key,
            lesson=lesson,
            defaults={'completed': True}
        )
        
        if not created and not progress.completed:
            progress.completed = True
            progress.save()
        
        # Получаем следующий урок для перенаправления
        all_lessons = list(Lesson.objects.filter(course='neuro').order_by('order'))
        next_lesson = None
        
        for i, l in enumerate(all_lessons):
            if l.id == lesson.id and i < len(all_lessons) - 1:
                next_lesson = all_lessons[i + 1]
                break
        
        response_data = {
            'status': 'success',
            'message': 'Урок отмечен как пройденный',
            'total_completed': UserProgress.objects.filter(
                session_key=request.session.session_key,
                completed=True
            ).count()
        }
        
        if next_lesson:
            if next_lesson.lesson_type == 'article':
                next_url = reverse('neuro_lesson_detail', args=[next_lesson.id])
            else:
                next_url = reverse('neuro_test_detail', args=[next_lesson.id])
            response_data['next_url'] = next_url
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def neuro_progress(request):

    if not request.session.session_key:
        request.session.save()
    
    completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        completed=True,
        lesson__course='neuro'
    ).select_related('lesson')
    
    total_lessons = Lesson.objects.filter(course='neuro').count()
    
    context = {
        'title': 'Мой прогресс',
        'completed_lessons': completed,
        'total_lessons': total_lessons,
        'completed_count': completed.count(),
    }
    
    return render(request, 'learningbase/neuro_progress.html', context)

@login_required
def neuro_results(request):
    """Финальная страница с результатами курса"""
    if not request.session.session_key:
        request.session.save()
    
    completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        completed=True,
        lesson__course='neuro'
    ).count()
    
    total = Lesson.objects.filter(course='neuro').count()
    
    context = {
        'title': 'Результаты курса',
        'completed': completed,
        'total': total,
        'percentage': (completed / total * 100) if total > 0 else 0,
    }
    
    return render(request, 'learningbase/neuro_results.html', context)

@login_required
def ethernet_start(request):
    """Главная страница курса Ethernet"""
    # Получаем или создаем сессию пользователя
    if not request.session.session_key:
        request.session.save()
    
    # Получаем все уроки курса ethernet
    lessons = Lesson.objects.filter(course='ethernet').prefetch_related('questions__answers').order_by('order')
    
    # Отдельно получаем статьи и тесты для нумерации
    articles = Lesson.objects.filter(course='ethernet', lesson_type='article').order_by('order')
    tests = Lesson.objects.filter(course='ethernet', lesson_type='test').order_by('order')
    
    # Создаем словари для хранения номеров
    article_numbers = {}
    test_numbers = {}
    
    for i, article in enumerate(articles, 1):
        article_numbers[article.id] = i
    
    for i, test in enumerate(tests, 1):
        test_numbers[test.id] = i
    
    # Получаем прогресс пользователя
    completed_lessons = UserProgress.objects.filter(
        session_key=request.session.session_key,
        completed=True,
        lesson__course='ethernet'
    ).values_list('lesson_id', flat=True)
    
    for lesson in lessons:
        lesson.completed = lesson.id in completed_lessons
        # Добавляем номер в зависимости от типа
        if lesson.lesson_type == 'article':
            lesson.display_number = article_numbers.get(lesson.id, '?')
            lesson.display_type = 'Статья'
        else:
            lesson.display_number = test_numbers.get(lesson.id, '?')
            lesson.display_type = 'Тест'
    
    context = {
        'title': 'Безопасное пользовние интернетом',
        'lessons': lessons,
        'completed_count': len(completed_lessons),
        'total_lessons': lessons.count(),
        'articles_count': articles.count(),
        'tests_count': tests.count(),
    }
    
    return render(request, 'learningbase/ethernet-start.html', context)

@login_required
def ethernet_lesson_detail(request, lesson_id):
    """Детальная страница урока (статья) для Ethernet"""
    if not request.session.session_key:
        request.session.save()
    
    lesson = get_object_or_404(Lesson, id=lesson_id, course='ethernet')
    
    # Проверяем, завершен ли урок
    is_completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        lesson=lesson,
        completed=True
    ).exists()
    
    # Получаем все уроки для навигации
    all_lessons = list(Lesson.objects.filter(course='ethernet').order_by('order'))
    current_index = None
    
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
            break
    
    # Получаем все статьи для нумерации
    all_articles = Lesson.objects.filter(course='ethernet', lesson_type='article').order_by('order')
    article_numbers = {}
    for i, article in enumerate(all_articles, 1):
        article_numbers[article.id] = i
    
    prev_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    context = {
        'title': lesson.title,
        'lesson': lesson,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'all_lessons': all_lessons,
        'current_index': current_index + 1,
        'total_lessons': len(all_lessons),
        'current_article_number': article_numbers.get(lesson.id, 1),
        'total_articles': all_articles.count(),
    }
    
    return render(request, 'learningbase/ethernet_lesson.html', context)

@login_required
def ethernet_test_detail(request, test_id):
    """Страница с тестом для Ethernet"""
    if not request.session.session_key:
        request.session.save()
    
    lesson = get_object_or_404(Lesson, id=test_id, course='ethernet', lesson_type='test')
    questions = lesson.questions.prefetch_related('answers').all()
    
    # Проверяем, завершен ли тест
    is_completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        lesson=lesson,
        completed=True
    ).exists()
    
    # Получаем все уроки для навигации
    all_lessons = list(Lesson.objects.filter(course='ethernet').order_by('order'))
    current_index = None
    
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
            break
    
    # Получаем все тесты для нумерации
    all_tests = Lesson.objects.filter(course='ethernet', lesson_type='test').order_by('order')
    test_numbers = {}
    for i, test in enumerate(all_tests, 1):
        test_numbers[test.id] = i
    
    prev_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    context = {
        'title': lesson.title,
        'lesson': lesson,
        'questions': questions,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'current_index': current_index + 1,
        'total_lessons': len(all_lessons),
        'current_test_number': test_numbers.get(lesson.id, 1),
        'total_tests': all_tests.count(),
    }
    
    return render(request, 'learningbase/ethernet_test.html', context)

@login_required
def ethernet_mark_complete(request, lesson_id):
    """Отметить урок Ethernet как пройденный"""
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.save()
        
        lesson = get_object_or_404(Lesson, id=lesson_id, course='ethernet')
        
        # Создаем или обновляем запись о прогрессе
        progress, created = UserProgress.objects.get_or_create(
            session_key=request.session.session_key,
            lesson=lesson,
            defaults={'completed': True}
        )
        
        if not created and not progress.completed:
            progress.completed = True
            progress.save()
        
        # Получаем следующий урок для перенаправления
        all_lessons = list(Lesson.objects.filter(course='ethernet').order_by('order'))
        next_lesson = None
        
        for i, l in enumerate(all_lessons):
            if l.id == lesson.id and i < len(all_lessons) - 1:
                next_lesson = all_lessons[i + 1]
                break
        
        response_data = {
            'status': 'success',
            'message': 'Урок отмечен как пройденный',
            'total_completed': UserProgress.objects.filter(
                session_key=request.session.session_key,
                completed=True
            ).count()
        }
        
        if next_lesson:
            if next_lesson.lesson_type == 'article':
                next_url = reverse('ethernet_lesson_detail', args=[next_lesson.id])
            else:
                next_url = reverse('ethernet_test_detail', args=[next_lesson.id])
            response_data['next_url'] = next_url
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def ethernet_check_answer(request):
    """Проверка ответа на вопрос для Ethernet (AJAX)"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        try:
            answer = TestAnswer.objects.get(id=answer_id, question_id=question_id)
            
            if answer.is_correct:
                return JsonResponse({
                    'correct': True,
                    'message': 'Правильно!',
                    'question_id': question_id
                })
            else:
                return JsonResponse({
                    'correct': False,
                    'message': 'Неправильно. Попробуй еще!'
                })
                
        except TestAnswer.DoesNotExist:
            return JsonResponse({'error': 'Ответ не найден'}, status=404)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def prompteng_start(request):
    """Главная страница курса Prompt Engineering"""
    if not request.session.session_key:
        request.session.save()
    
    lessons = Lesson.objects.filter(course='prompt').prefetch_related('questions__answers').order_by('order')
    
    articles = Lesson.objects.filter(course='prompt', lesson_type='article').order_by('order')
    tests = Lesson.objects.filter(course='prompt', lesson_type='test').order_by('order')
    
    article_numbers = {}
    test_numbers = {}
    
    for i, article in enumerate(articles, 1):
        article_numbers[article.id] = i
    
    for i, test in enumerate(tests, 1):
        test_numbers[test.id] = i
    
    completed_lessons = UserProgress.objects.filter(
        session_key=request.session.session_key,
        completed=True,
        lesson__course='prompt'
    ).values_list('lesson_id', flat=True)
    
    for lesson in lessons:
        lesson.completed = lesson.id in completed_lessons
        if lesson.lesson_type == 'article':
            lesson.display_number = article_numbers.get(lesson.id, '?')
            lesson.display_type = 'Статья'
        else:
            lesson.display_number = test_numbers.get(lesson.id, '?')
            lesson.display_type = 'Тест'
    
    context = {
        'title': 'Инженер промптов',
        'lessons': lessons,
        'completed_count': len(completed_lessons),
        'total_lessons': lessons.count(),
        'articles_count': articles.count(),
        'tests_count': tests.count(),
    }
    
    return render(request, 'learningbase/prompteng_start.html', context)

@login_required
def prompteng_lesson_detail(request, lesson_id):
    """Детальная страница урока (статья) для Prompt Engineering"""
    if not request.session.session_key:
        request.session.save()
    
    lesson = get_object_or_404(Lesson, id=lesson_id, course='prompt', lesson_type='article')
    
    is_completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        lesson=lesson,
        completed=True
    ).exists()
    
    all_lessons = list(Lesson.objects.filter(course='prompt').order_by('order'))
    current_index = None
    
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
            break
    
    all_articles = Lesson.objects.filter(course='prompt', lesson_type='article').order_by('order')
    article_numbers = {}
    for i, article in enumerate(all_articles, 1):
        article_numbers[article.id] = i
    
    prev_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    context = {
        'title': lesson.title,
        'lesson': lesson,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'all_lessons': all_lessons,
        'current_index': current_index + 1,
        'total_lessons': len(all_lessons),
        'current_article_number': article_numbers.get(lesson.id, 1),
        'total_articles': all_articles.count(),
    }
    
    return render(request, 'learningbase/prompteng_lesson.html', context)

@login_required
def prompteng_test_detail(request, test_id):
    """Страница с тестом для Prompt Engineering"""
    if not request.session.session_key:
        request.session.save()
    
    lesson = get_object_or_404(Lesson, id=test_id, course='prompt', lesson_type='test')
    questions = lesson.questions.prefetch_related('answers').all()
    
    is_completed = UserProgress.objects.filter(
        session_key=request.session.session_key,
        lesson=lesson,
        completed=True
    ).exists()
    
    all_lessons = list(Lesson.objects.filter(course='prompt').order_by('order'))
    current_index = None
    
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
            break
    
    all_tests = Lesson.objects.filter(course='prompt', lesson_type='test').order_by('order')
    test_numbers = {}
    for i, test in enumerate(all_tests, 1):
        test_numbers[test.id] = i
    
    prev_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    context = {
        'title': lesson.title,
        'lesson': lesson,
        'questions': questions,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'current_index': current_index + 1,
        'total_lessons': len(all_lessons),
        'current_test_number': test_numbers.get(lesson.id, 1),
        'total_tests': all_tests.count(),
    }
    
    return render(request, 'learningbase/prompteng_test.html', context)

@login_required
def prompteng_check_answer(request):
    """Проверка ответа на вопрос для Prompt Engineering (AJAX)"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        try:
            answer = TestAnswer.objects.get(id=answer_id, question_id=question_id)
            
            if answer.is_correct:
                return JsonResponse({
                    'correct': True,
                    'message': 'Правильно!',
                    'question_id': question_id
                })
            else:
                return JsonResponse({
                    'correct': False,
                    'message': 'Неправильно. Попробуй еще!'
                })
                
        except TestAnswer.DoesNotExist:
            return JsonResponse({'error': 'Ответ не найден'}, status=404)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def prompteng_mark_complete(request, lesson_id):
    """Отметить урок Prompt Engineering как пройденный"""
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.save()
        
        lesson = get_object_or_404(Lesson, id=lesson_id, course='prompt')
        
        progress, created = UserProgress.objects.get_or_create(
            session_key=request.session.session_key,
            lesson=lesson,
            defaults={'completed': True}
        )
        
        if not created and not progress.completed:
            progress.completed = True
            progress.save()
        
        all_lessons = list(Lesson.objects.filter(course='prompt').order_by('order'))
        next_lesson = None
        
        for i, l in enumerate(all_lessons):
            if l.id == lesson.id and i < len(all_lessons) - 1:
                next_lesson = all_lessons[i + 1]
                break
        
        response_data = {
            'status': 'success',
            'message': 'Урок отмечен как пройденный',
            'total_completed': UserProgress.objects.filter(
                session_key=request.session.session_key,
                completed=True
            ).count()
        }
        
        if next_lesson:
            if next_lesson.lesson_type == 'article':
                next_url = reverse('prompteng_lesson_detail', args=[next_lesson.id])
            else:
                next_url = reverse('prompteng_test_detail', args=[next_lesson.id])
            response_data['next_url'] = next_url
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
# Авторизация и регистрация

def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Правильно заполните поля')
    else:
        form = RegisterForm()
    
    return render(request, 'learningbase/auth/register.html', {'form': form})

def login_view(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Перенаправляем на предыдущую страницу или на главную
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            messages.error(request, 'Правильно заполните поля')
    else:
        form = LoginForm()
    
    return render(request, 'learningbase/auth/login.html', {'form': form})

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('home')

@login_required
def profile_view(request):
    """Профиль пользователя с реальным прогрессом"""
    # Получаем прогресс пользователя по всем курсам
    user_progress = UserProgress.objects.filter(
        session_key=request.session.session_key,
        completed=True
    ).select_related('lesson')
    
    # Считаем общее количество пройденных уроков
    total_completed = user_progress.count()
    
    # Считаем прогресс по каждому курсу отдельно
    neuro_lessons_total = Lesson.objects.filter(course='neuro').count()
    neuro_completed = user_progress.filter(lesson__course='neuro').count()
    
    ethernet_lessons_total = Lesson.objects.filter(course='ethernet').count()
    ethernet_completed = user_progress.filter(lesson__course='ethernet').count()
    
    prompt_lessons_total = Lesson.objects.filter(course='prompt').count()
    prompt_completed = user_progress.filter(lesson__course='prompt').count()
    
    # Создаем список последних пройденных уроков
    recent_lessons = user_progress.order_by('-completed_at')[:5]
    
    context = {
        'title': 'Профиль',
        'total_completed': total_completed,
        'neuro_progress': {
            'total': neuro_lessons_total,
            'completed': neuro_completed,
            'percentage': (neuro_completed / neuro_lessons_total * 100) if neuro_lessons_total > 0 else 0
        },
        'ethernet_progress': {
            'total': ethernet_lessons_total,
            'completed': ethernet_completed,
            'percentage': (ethernet_completed / ethernet_lessons_total * 100) if ethernet_lessons_total > 0 else 0
        },
        'prompt_progress': {
            'total': prompt_lessons_total,
            'completed': prompt_completed,
            'percentage': (prompt_completed / prompt_lessons_total * 100) if prompt_lessons_total > 0 else 0
        },
        'recent_lessons': recent_lessons,
    }
    
    return render(request, 'learningbase/auth/profile.html', context)