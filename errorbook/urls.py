from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('questions/', views.question_list, name='question_list'),
    path('import/', views.import_question, name='import_question'),
    path('import/upload/', views.upload_question, name='upload_question'),
    path('question/<int:qid>/', views.question_detail, name='question_detail'),
    path('question/<int:qid>/edit/', views.question_edit, name='question_edit'),
    path('question/<int:qid>/delete/', views.question_delete, name='question_delete'),
    path('review/', views.review_start, name='review_start'),
    path('review/<int:qid>/', views.review_question, name='review_question'),
    path('review/<int:qid>/check/', views.review_check, name='review_check'),
    path('review/<int:qid>/result/', views.review_result, name='review_result'),
    path('stats/', views.stats, name='stats'),
    path('knowledge-graph/', views.knowledge_graph, name='knowledge_graph'),
    path('api/random/', views.api_random_question, name='api_random'),
    path('api/generate-question/<int:qid>/', views.api_generate_question, name='api_generate'),

]
