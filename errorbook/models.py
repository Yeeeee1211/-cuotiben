from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    """错题主表"""
    ERROR_TYPE_CHOICES = [
        ('concept', '概念模糊'),
        ('calculation', '计算失误'),
        ('reading', '审题偏差'),
        ('method', '方法错误'),
        ('blind_spot', '知识盲区'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='学生')
    title = models.CharField(max_length=200, verbose_name='题目名称', blank=True, default='')
    subject = models.CharField(max_length=20, verbose_name='学科', blank=True, default='')
    knowledge_point = models.CharField(max_length=100, verbose_name='知识点', blank=True, default='')
    difficulty = models.CharField(max_length=10, verbose_name='难度', choices=DIFFICULTY_CHOICES, blank=True, default='')
    error_type = models.CharField(max_length=20, verbose_name='错误类型', choices=ERROR_TYPE_CHOICES, blank=True, default='')
    question_text = models.TextField(verbose_name='题目内容', blank=True, default='')
    answer_text = models.TextField(verbose_name='正确答案', blank=True, default='')
    original_image = models.ImageField(upload_to='questions/', verbose_name='原始图片')
    ocr_raw_text = models.TextField(verbose_name='OCR原始文本', blank=True, default='')
    ai_analysis_json = models.TextField(verbose_name='AI分析JSON', blank=True, default='')
    review_count = models.IntegerField(default=0, verbose_name='复习次数')
    next_review_date = models.DateTimeField(null=True, blank=True, verbose_name='下次复习日期')
    last_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='最后复习时间')
    is_mastered = models.BooleanField(default=False, verbose_name='是否已掌握')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='导入时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '错题'
        verbose_name_plural = '错题'

    def __str__(self):
        return self.title or f'错题 #{self.id}'


class ReviewRecord(models.Model):
    """复习记录表"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='错题')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='学生')
    student_answer = models.TextField(verbose_name='学生回答', blank=True, default='')
    is_correct = models.BooleanField(null=True, verbose_name='是否正确')
    ai_feedback = models.TextField(verbose_name='AI批改反馈', blank=True, default='')
    ai_score = models.CharField(max_length=20, verbose_name='AI评分', blank=True, default='')
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name='复习时间')

    class Meta:
        ordering = ['-reviewed_at']
        verbose_name = '复习记录'
        verbose_name_plural = '复习记录'

    def __str__(self):
        return f'{self.user.username} 复习 #{self.question.id}'
