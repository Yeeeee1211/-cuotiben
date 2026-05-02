import json
import uuid
import os
from datetime import datetime, timedelta
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.db.models import Count, Q

from .models import Question, ReviewRecord
from .ocr import recognize_text
from .ai_agent import analyze_question, review_answer, generate_similar_question


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


@login_required
def index(request):
    """仪表盘首页"""
    questions = Question.objects.filter(user=request.user)
    total = questions.count()
    reviewed = ReviewRecord.objects.filter(user=request.user).values('question').distinct().count()
    subjects = questions.values('subject').annotate(count=Count('id')).order_by('-count')

    # 艾宾浩斯：今日到期
    now = timezone.now()
    due_today = questions.filter(
        next_review_date__isnull=False,
        next_review_date__lte=now
    ).count()

    # 掌握度
    mastered = questions.filter(is_mastered=True).count()
    mastery_pct = round(mastered / total * 100, 1) if total > 0 else 0

    # cat 头鹰宠物 XP
    from datetime import date
    total_reviews = ReviewRecord.objects.filter(user=request.user).count()
    correct_reviews = ReviewRecord.objects.filter(user=request.user, is_correct=True).count()
    xp = total * 10 + total_reviews * 5 + correct_reviews * 10
    level = xp // 100 + 1
    xp_pct = round(xp % 100)
    level_xp = level * 100

    recent = questions[:5]

    context = {
        'total_questions': total,
        'total_reviewed': reviewed,
        'due_today': due_today,
        'mastered': mastered,
        'mastery_pct': mastery_pct,
        'level': level,
        'xp': xp,
        'xp_pct': xp_pct,
        'level_xp': level_xp,
        'subjects': [(s['subject'] or '未分类', s['count']) for s in subjects],
        'recent_questions': recent,
    }
    return render(request, 'errorbook/index.html', context)


@login_required
def question_list(request):
    """错题列表，支持筛选"""
    questions = Question.objects.filter(user=request.user)

    subject = request.GET.get('subject', '')
    error_type = request.GET.get('error_type', '')
    difficulty = request.GET.get('difficulty', '')
    search = request.GET.get('search', '')
    kp = request.GET.get('kp', '')

    if subject:
        questions = questions.filter(subject=subject)
    if error_type:
        questions = questions.filter(error_type=error_type)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if kp:
        from .knowledge_points import _ALIAS_MAP, classify_knowledge_point
        if kp == '其他未归类':
            # 筛选出无法归类到任何一级知识点的题目
            unclassified_ids = [
                q.id for q in questions
                if classify_knowledge_point(q.knowledge_point, subject) is None
            ]
            questions = questions.filter(id__in=unclassified_ids)
        else:
            aliases = _ALIAS_MAP.get(subject, {}).get(kp, [])
            if aliases:
                kp_q = Q(knowledge_point__icontains=kp)
                for alias in aliases:
                    kp_q |= Q(knowledge_point__icontains=alias)
                questions = questions.filter(kp_q)
            else:
                questions = questions.filter(knowledge_point__icontains=kp)
    if search:
        questions = questions.filter(
            Q(title__icontains=search) | Q(question_text__icontains=search) | Q(knowledge_point__icontains=search)
        )

    context = {
        'questions': questions,
        'current_subject': subject,
        'current_error_type': error_type,
        'current_difficulty': difficulty,
        'search': search,
        'kp': kp,
    }
    if _is_ajax(request):
        return render(request, 'errorbook/_question_list.html', context)
    return render(request, 'errorbook/question_list.html', context)


@login_required
def question_detail(request, qid):
    """错题详情"""
    question = get_object_or_404(Question, id=qid, user=request.user)
    reviews = ReviewRecord.objects.filter(question=question, user=request.user)[:10]
    return render(request, 'errorbook/question_detail.html', {
        'question': question,
        'reviews': reviews,
    })


@login_required
def import_question(request):
    """导入错题页"""
    if _is_ajax(request):
        return render(request, 'errorbook/_import.html')
    return render(request, 'errorbook/import.html')


@login_required
def upload_question(request):
    """处理上传 -> OCR -> AI分析 -> 入库"""
    if request.method != 'POST':
        return redirect('import_question')

    if 'image' not in request.FILES:
        return render(request, 'errorbook/import.html', {'error': '请选择图片'})

    image_file = request.FILES['image']
    ext = os.path.splitext(image_file.name)[1] or '.jpg'
    filename = f'{uuid.uuid4().hex}{ext}'
    save_path = os.path.join(settings.MEDIA_ROOT, 'questions', filename)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    question = Question.objects.create(
        user=request.user,
        original_image=f'questions/{filename}',
    )

    # OCR 识别
    ocr_text = ''
    ocr_error = None
    try:
        ocr_text = recognize_text(save_path)
        question.ocr_raw_text = ocr_text
        question.save()
    except Exception as e:
        ocr_error = str(e)

    # AI 分析
    analysis_result = None
    ai_error = None
    if ocr_text and not ocr_error:
        try:
            analysis_result = analyze_question(ocr_text)
            if analysis_result:
                question.title = analysis_result.get('title', '')
                question.subject = analysis_result.get('subject', '')
                question.knowledge_point = analysis_result.get('knowledge_point', '')
                difficulty_map = {'简单': 'easy', '中等': 'medium', '困难': 'hard'}
                d = analysis_result.get('difficulty', '')
                question.difficulty = difficulty_map.get(d, d)
                error_type_map = {
                    '概念模糊': 'concept', '计算失误': 'calculation',
                    '审题偏差': 'reading', '方法错误': 'method', '知识盲区': 'blind_spot'
                }
                et = analysis_result.get('error_type', '')
                question.error_type = error_type_map.get(et, et)
                question.question_text = analysis_result.get('question_text', '')
                question.answer_text = analysis_result.get('answer_text', '')
                question.ai_analysis_json = json.dumps(analysis_result, ensure_ascii=False)
                question.save()
        except Exception as e:
            ai_error = str(e)

    return render(request, 'errorbook/import_result.html', {
        'question': question,
        'ocr_text': ocr_text,
        'ocr_error': ocr_error,
        'analysis': analysis_result,
        'ai_error': ai_error,
    })


@login_required
def question_edit(request, qid):
    """编辑错题信息"""
    question = get_object_or_404(Question, id=qid, user=request.user)
    if request.method == 'POST':
        question.title = request.POST.get('title', question.title)
        question.subject = request.POST.get('subject', question.subject)
        question.knowledge_point = request.POST.get('knowledge_point', question.knowledge_point)
        question.difficulty = request.POST.get('difficulty', question.difficulty)
        question.error_type = request.POST.get('error_type', question.error_type)
        question.question_text = request.POST.get('question_text', question.question_text)
        question.answer_text = request.POST.get('answer_text', question.answer_text)
        question.save()
        return redirect('question_detail', qid=qid)
    subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
    return render(request, 'errorbook/question_edit.html', {
        'question': question,
        'subjects': subjects,
    })


@login_required
def question_delete(request, qid):
    """删除错题"""
    question = get_object_or_404(Question, id=qid, user=request.user)
    if request.method == 'POST':
        if question.original_image and os.path.exists(question.original_image.path):
            os.remove(question.original_image.path)
        question.delete()
    return redirect('question_list')


@login_required
def review_start(request):
    """复习模式入口 - 选择错题"""
    questions = Question.objects.filter(user=request.user)

    # 艾宾浩斯：今日 / 本周到期
    now = timezone.now()
    due_today_qs = questions.filter(
        next_review_date__isnull=False,
        next_review_date__lte=now
    )
    due_week_qs = questions.filter(
        next_review_date__isnull=False,
        next_review_date__lte=now + timedelta(days=7)
    )

    # 各区间分布
    from .spaced_repetition import INTERVALS
    interval_dist = []
    for i, days in enumerate(INTERVALS):
        cnt = questions.filter(review_count=i, next_review_date__isnull=False).count()
        interval_dist.append({'label': f'{days}天', 'days': days, 'count': cnt})

    # 日历数据：本月每日复习任务
    import calendar
    now = timezone.now()
    year, month = now.year, now.month
    _, last_day = calendar.monthrange(year, month)
    first_weekday = (datetime(year, month, 1).weekday() + 1) % 7  # 0=周日

    review_dates = questions.filter(
        next_review_date__isnull=False,
        next_review_date__year=year,
        next_review_date__month=month
    ).values('id', 'title', 'subject', 'next_review_date').order_by('next_review_date')

    # 按日分组: {day: [questions]}
    day_questions = {}
    for r in review_dates:
        day = r['next_review_date'].day
        if day not in day_questions:
            day_questions[day] = []
        day_questions[day].append({
            'id': r['id'],
            'title': r['title'],
            'subject': r['subject'],
        })

    # 构建日历网格: 每周7天
    calendar_weeks = []
    week = [None] * first_weekday  # 月初空白格
    for d in range(1, last_day + 1):
        week.append({'day': d, 'count': len(day_questions.get(d, [])), 'questions': day_questions.get(d, [])})
        if len(week) == 7:
            calendar_weeks.append(week)
            week = []
    if week:
        while len(week) < 7:
            week.append(None)
        calendar_weeks.append(week)

    month_label = f'{year}年{month}月'

    subject = request.GET.get('subject', '')
    error_type = request.GET.get('error_type', '')
    if subject:
        questions = questions.filter(subject=subject)
    if error_type:
        questions = questions.filter(error_type=error_type)

    context = {
        'questions': questions,
        'due_today': due_today_qs,
        'due_week_count': due_week_qs.count(),
        'due_today_count': due_today_qs.count(),
        'interval_dist': interval_dist,
        'current_subject': subject,
        'current_error_type': error_type,
        'calendar_weeks': calendar_weeks,
        'month_label': month_label,
        'today': now.day,
    }
    if _is_ajax(request):
        return render(request, 'errorbook/_review.html', context)
    return render(request, 'errorbook/review.html', context)


@login_required
def review_question(request, qid):
    """出示指定错题供学生作答"""
    question = get_object_or_404(Question, id=qid, user=request.user)
    return render(request, 'errorbook/review_question.html', {
        'question': question,
    })


@login_required
def review_check(request, qid):
    """AI批改学生作答"""
    from .spaced_repetition import parse_score, compute_next_review

    question = get_object_or_404(Question, id=qid, user=request.user)
    if request.method != 'POST':
        return redirect('review_question', qid=qid)

    student_answer = request.POST.get('student_answer', '').strip()

    record = ReviewRecord.objects.create(
        question=question,
        user=request.user,
        student_answer=student_answer,
    )

    # AI 批改
    try:
        result = review_answer(question.question_text, question.answer_text, student_answer)
        if result:
            record.is_correct = result.get('is_correct', False)
            record.ai_feedback = result.get('feedback', '')
            record.ai_score = result.get('score', '')
            record.save()
    except Exception:
        record.ai_feedback = 'AI批改服务暂时不可用，请稍后再试。'
        record.save()

    # 艾宾浩斯遗忘曲线 + 掌握度追踪
    score_int = parse_score(record.ai_score)
    if score_int is not None:
        new_count, interval_days = compute_next_review(score_int, question.review_count)
        question.review_count = new_count
        question.next_review_date = timezone.now() + timedelta(days=interval_days)
        question.last_reviewed_at = timezone.now()

        if score_int >= 80:
            question.is_mastered = True
        elif score_int < 60 and question.is_mastered:
            question.is_mastered = False

        question.save()

    return redirect('review_result', qid=qid)


@login_required
def review_result(request, qid):
    """展示批改结果"""
    question = get_object_or_404(Question, id=qid, user=request.user)
    record = ReviewRecord.objects.filter(question=question, user=request.user).last()
    return render(request, 'errorbook/review_result.html', {
        'question': question,
        'record': record,
    })


@login_required
def stats(request):
    """学习统计"""
    questions = Question.objects.filter(user=request.user)
    total = questions.count()

    subject_stats = questions.values('subject').annotate(count=Count('id')).order_by('-count')
    _et_stats = questions.values('error_type').annotate(count=Count('id')).order_by('-count')
    error_type_stats = [{'error_type': s['error_type'], 'display': dict(Question.ERROR_TYPE_CHOICES).get(s['error_type'], '未分类'), 'count': s['count']} for s in _et_stats]

    _df_stats = questions.values('difficulty').annotate(count=Count('id')).order_by('-count')
    difficulty_stats = [{'difficulty': s['difficulty'], 'display': dict(Question.DIFFICULTY_CHOICES).get(s['difficulty'], '未评估'), 'count': s['count']} for s in _df_stats]

    reviewed_count = ReviewRecord.objects.filter(user=request.user).values('question').distinct().count()
    correct_count = ReviewRecord.objects.filter(user=request.user, is_correct=True).values('question').distinct().count()
    mastered_count = questions.filter(is_mastered=True).count()
    mastery_rate = round(mastered_count / total * 100, 1) if total > 0 else 0

    # 复习区间分布
    from .spaced_repetition import INTERVALS
    interval_dist = []
    for i, days in enumerate(INTERVALS):
        cnt = questions.filter(review_count=i, next_review_date__isnull=False).count()
        interval_dist.append({'label': f'{days}天复习', 'count': cnt})

    context = {
        'total': total,
        'reviewed_count': reviewed_count,
        'correct_count': correct_count,
        'mastered_count': mastered_count,
        'mastery_rate': mastery_rate,
        'accuracy': round(correct_count / reviewed_count * 100, 1) if reviewed_count > 0 else 0,
        'subject_stats': subject_stats,
        'error_type_stats': error_type_stats,
        'difficulty_stats': difficulty_stats,
        'interval_dist': interval_dist,
    }
    if _is_ajax(request):
        return render(request, 'errorbook/_stats.html', context)
    return render(request, 'errorbook/stats.html', context)


@login_required
def knowledge_graph(request):
    """知识图谱 — 按学科展示知识点掌握情况"""
    from .knowledge_points import KNOWLEDGE_TREE, classify_knowledge_point

    questions = Question.objects.filter(user=request.user)

    # 按学科统计实际错题总数
    subject_totals = {}
    for row in questions.values('subject').annotate(count=Count('id')):
        subj = row['subject']
        if subj and subj in KNOWLEDGE_TREE:
            subject_totals[subj] = row['count']

    # 按学科→知识点聚合，然后归类到一级知识点
    kp_rows = questions.values('subject', 'knowledge_point').annotate(count=Count('id'))
    kp_lookup = {}  # {(subject, first_level_kp): count}
    other_lookup = {}  # {subject: count} — 未归类知识点
    for row in kp_rows:
        subj = row['subject']
        kp = row['knowledge_point']
        if not subj or not kp:
            continue
        first_level = classify_knowledge_point(kp, subj)
        if first_level:
            key = (subj, first_level)
            kp_lookup[key] = kp_lookup.get(key, 0) + row['count']
        else:
            other_lookup[subj] = other_lookup.get(subj, 0) + row['count']

    graph_data = []
    for subject, kps in KNOWLEDGE_TREE.items():
        items = []
        for kp in kps:
            count = kp_lookup.get((subject, kp), 0)
            if count <= 2:
                color = 'green'
            elif count <= 5:
                color = 'yellow'
            else:
                color = 'red'
            items.append({'name': kp, 'count': count, 'color': color})
        other_count = other_lookup.get(subject, 0)
        if other_count > 0:
            items.append({'name': '其他未归类', 'count': other_count, 'color': 'green'})
        graph_data.append({'subject': subject, 'items': items, 'total': subject_totals.get(subject, 0)})

    tmpl = 'errorbook/_knowledge_graph.html' if _is_ajax(request) else 'errorbook/knowledge_graph.html'
    return render(request, tmpl, {
        'graph_data': graph_data,
        'subject_totals': subject_totals,
    })


@login_required
def api_generate_question(request, qid):
    """AJAX: 根据错题生成变式题"""
    question = get_object_or_404(Question, id=qid, user=request.user)

    if not question.question_text or not question.answer_text:
        return JsonResponse({'error': '该题目缺少文字内容或答案，无法生成变式题'}, status=400)

    try:
        result = generate_similar_question(
            question.question_text,
            question.answer_text,
            question.subject,
            question.knowledge_point,
            has_image=bool(question.original_image)
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_random_question(request):
    """AJAX: 获取随机一道错题"""
    questions = Question.objects.filter(user=request.user)
    subject = request.GET.get('subject', '')
    if subject:
        questions = questions.filter(subject=subject)

    question = questions.order_by('?').first()
    if not question:
        return JsonResponse({'error': '暂无错题'}, status=404)
    return JsonResponse({
        'id': question.id,
        'title': question.title,
        'subject': question.subject,
        'knowledge_point': question.knowledge_point,
    })
