from django.contrib import admin
from .models import Question, ReviewRecord

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subject', 'difficulty', 'error_type', 'user', 'created_at']
    list_filter = ['subject', 'difficulty', 'error_type']
    search_fields = ['title', 'question_text']

@admin.register(ReviewRecord)
class ReviewRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'user', 'is_correct', 'reviewed_at']
    list_filter = ['is_correct']
