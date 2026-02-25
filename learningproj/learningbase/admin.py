from django.contrib import admin
from .models import Lesson, TestQuestion, TestAnswer, UserProgress, Post

class TestAnswerInline(admin.TabularInline):
    model = TestAnswer
    extra = 4

class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['course', 'order', 'title', 'lesson_type']
    list_display_links = ['title']
    list_editable = ['order']
    list_filter = ['course', 'lesson_type']
    search_fields = ['title', 'content']
    inlines = [TestQuestionInline]

@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'question_text', 'order']
    list_editable = ['order']
    list_filter = ['lesson__course']
    search_fields = ['question_text']
    inlines = [TestAnswerInline]

@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer_text', 'is_correct']
    list_editable = ['is_correct']
    list_filter = ['question__lesson__course']

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed', 'lesson__course']
    search_fields = ['session_key']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['name', 'time_update','time_create']
    search_fields = ['name', 'content']
