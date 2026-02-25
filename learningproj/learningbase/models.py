from django.db import models
from django.urls import reverse

# Create your models here.
class Post(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название')
    content = models.TextField(blank=True, verbose_name='Контент')
    slug = models.SlugField(max_length=100, db_index=True, verbose_name='Слаг')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата-создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')
    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("post", kwargs={"post_slug": self.slug})


class Lesson(models.Model):
    COURSE_CHOICES = (
        ('neuro', 'Нейросети для начинающих'),
        ('ethernet', 'Безопасное пользование интернетом'),
        ('prompt', 'Инженер промптов'),
    )
    
    LESSON_TYPES = (
        ('article', 'Статья'),
        ('test', 'Тест'),
    )
    
    course = models.CharField(max_length=20, choices=COURSE_CHOICES, default='neuro', verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Название урока")
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPES, default='article', verbose_name="Тип урока")
    content = models.TextField(blank=True, verbose_name="Содержание статьи")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['course', 'order']
    
    def __str__(self):
        return f"[{self.get_course_display()}] {self.order}. {self.title}"

class TestQuestion(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions', verbose_name="Урок")
    question_text = models.CharField(max_length=500, verbose_name="Вопрос")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = 'Вопрос теста'
        verbose_name_plural = 'Вопросы теста'
        ordering = ['order']
    
    def __str__(self):
        return self.question_text

class TestAnswer(models.Model):
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name="Вопрос")
    answer_text = models.CharField(max_length=300, verbose_name="Ответ")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    
    class Meta:
        verbose_name = 'Ответ теста'
        verbose_name_plural = 'Ответы теста'

    def __str__(self):
        return self.answer_text

class UserProgress(models.Model):
    session_key = models.CharField(max_length=100, verbose_name="Сессия пользователя")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Урок")
    completed = models.BooleanField(default=False, verbose_name="Завершено")
    completed_at = models.DateTimeField(auto_now=True, verbose_name="Дата завершения")
    
    class Meta:
        verbose_name = 'Прогресс'
        verbose_name_plural = 'Прогресс'
        unique_together = ['session_key', 'lesson']
    
    def __str__(self):
        return f"{self.session_key} - {self.lesson.title}"