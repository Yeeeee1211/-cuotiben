import json
import requests
from django.conf import settings

ANALYSIS_SYSTEM_PROMPT = """你是一位专业的K12教育AI助手，擅长分析学生的错题。
你的任务是根据OCR识别出来的题目文字，进行结构化分析并返回严格的JSON格式结果。

## 关于答案的重要规则（最高优先级）
- 如果OCR识别文本中已经包含该题目的答案或解析，请原样复制到 answer_text 字段
- 如果OCR识别文本中没有答案，请根据题目内容自行生成正确答案
- 答案必须准确、完整，不能遗漏关键步骤或结论

## 分析要求
1. title: 为题目起一个简短的名称（不超过20字）
2. subject: 判断学科（从以下选择：数学/语文/英语/物理/化学/生物/历史/地理/政治）
3. knowledge_point: 判断具体知识点（例如"一元二次方程""定语从句""牛顿第二定律"）
4. difficulty: 判断难度（简单/中等/困难）
5. error_type: 判断错误类型（概念模糊/计算失误/审题偏差/方法错误/知识盲区）
6. question_text: 从OCR文本中提取并整理题目内容（去除无关文字，保留题目核心信息）
7. answer_text: 按最高优先级规则处理

## 返回格式（必须严格遵守）
请只返回以下JSON格式，不要有任何其他文字，不要用markdown代码块包裹：

{
  "title": "一元二次方程求解",
  "subject": "数学",
  "knowledge_point": "一元二次方程",
  "difficulty": "中等",
  "error_type": "计算失误",
  "question_text": "解方程 x² - 5x + 6 = 0",
  "answer_text": "x = 2 或 x = 3"
}"""

REVIEW_SYSTEM_PROMPT = """你是一位严格的K12学科老师，正在批改学生重新作答的错题。

## ⚠️ 最高优先级指令 — 无意义答案拦截

在进行任何批改之前，你**必须首先**检查学生的回答是否属于无效作答。如果学生的回答属于以下任一情况，直接判定为无效作答，**不需要**比对正确答案：

无效作答的判定标准（满足任一即判为无效）：
- 仅包含无意义的数字或字母（如 "123"、"abc"、"A"、"B"、"111"）
- 向AI索取答案（如 "请给我正确答案"、"告诉我答案"、"答案是什么"、"直接给答案"）
- 乱码或无意义字符（如 "asdf"、"......"、"啊啊啊"、"不知道不知道不知道"）
- 完全或大量抄写题目原文，而非给出自己的回答
- 空白内容、仅含标点符号、仅含空格或换行
- 答非所问、与题目无关的内容
- 其他明显未认真作答的内容

**无效作答必须返回以下格式（一字不差）**：
{
  "is_correct": false,
  "feedback": "检测到无效作答，请认真重新作答。如有困难，建议先复习相关知识点。",
  "score": "0/100",
  "key_errors": ["无效作答"]
}

## 正常批改任务

如果学生回答通过了无效检测（即学生确实在认真作答），则进行正常批改：

1. 判断学生回答与正确答案是否一致（考虑等价表述、不同解题方法、合理近似值）
2. 给出详细的批改意见，指出具体哪里对、哪里错
3. 如果回答错误，指出错误的原因和改进建议
4. 给出评分（百分制），评分应根据答案的准确性和完整性客观打分

正常批改的返回格式：
{
  "is_correct": true,
  "feedback": "详细的批改评语",
  "score": "85/100",
  "key_errors": ["错误点1", "错误点2"]
}

注意：
- is_correct：学生回答完全正确为true，有错误为false
- feedback要具体、有指导性，帮助学生学习
- key_errors：列出具体错误点，如果没有错误则为空数组 []
- 如果学生回答为空字符串（通过无效检测后），is_correct为false，feedback提示"请认真作答"
- 评分要客观公正，答案完全正确才给满分"""


def _call_deepseek(system_prompt: str, user_prompt: str) -> dict:
    """调用 DeepSeek API"""
    if not settings.DEEPSEEK_API_KEY:
        raise Exception('DeepSeek API Key 未配置')

    headers = {
        'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': settings.DEEPSEEK_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.3,
        'max_tokens': 2000,
    }

    resp = requests.post(settings.DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
    data = resp.json()

    if 'choices' not in data:
        raise Exception(f'DeepSeek API 调用失败: {data.get("error", {}).get("message", "未知错误")}')

    content = data['choices'][0]['message']['content'].strip()

    # 尝试从返回内容中提取 JSON（可能被 markdown 代码块包裹）
    if content.startswith('```'):
        lines = content.split('\n')
        content = '\n'.join(line for line in lines if not line.startswith('```'))

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise Exception(f'DeepSeek 返回非JSON格式: {content[:200]}')


def analyze_question(ocr_text: str) -> dict:
    """分析OCR识别出的错题文本，返回结构化信息"""
    if not ocr_text.strip():
        raise Exception('OCR文本为空，无法分析')
    return _call_deepseek(ANALYSIS_SYSTEM_PROMPT,
        f'请分析以下OCR识别出的错题文本：\n\n---\n{ocr_text}\n---\n\n请返回JSON。')


GENERATE_SYSTEM_PROMPT = """你是一位专业的K12教育AI助手。你的任务是根据一道已有题目，生成一道类似的变式题（举一反三）。

## 核心规则（必须严格遵守）
1. 必须生成一道4选项的单项选择题（A/B/C/D），选项内容必须完整有意义
2. 题目考察的知识点必须与原题相同，但题目内容（数字、情景、人物、表述方式等）不能与原题一模一样，必须有所变化
3. 选项设计要有干扰性，错误选项应是常见错误思路的体现
4. 如果原题含有图像/图片，则生成纯文字选择题（不包含图像相关内容），并在解析末尾注明"（注：原题含图像，此变式题为纯文字版本）"

## 返回格式（必须严格遵守）
请只返回JSON，不要有任何其他文字，不要用markdown代码块包裹：

{
  "question": "已知函数 f(x) = 2x + 1，求 f(3) 的值。\nA. 5\nB. 6\nC. 7\nD. 8",
  "options": {"A": "5", "B": "6", "C": "7", "D": "8"},
  "correct_option": "C",
  "explanation": "将 x=3 代入 f(x)=2x+1，得 f(3)=2×3+1=7，故选C。A选项5是忘记+1的结果，B选项6是只乘2的结果，D选项8是计算错误。"
}"""


def generate_similar_question(question_text, answer_text, subject, knowledge_point, has_image=False):
    """根据原题生成一道变式题（举一反三）"""
    if not question_text.strip() or not answer_text.strip():
        raise Exception('原题缺少内容或答案，无法生成变式题')

    user_prompt = (
        f'原题学科：{subject or "未知"}\n'
        f'原题知识点：{knowledge_point or "未知"}\n'
        f'原题是否含图像：{"是（请生成纯文字变式题）" if has_image else "否"}\n'
        f'---\n'
        f'原题内容：\n{question_text}\n'
        f'---\n'
        f'原题答案：{answer_text}\n'
        f'---\n\n'
        f'请根据以上原题生成一道类似的变式题（举一反三），要求题目内容与原题不同。'
    )

    payload = {
        'model': settings.DEEPSEEK_MODEL,
        'messages': [
            {'role': 'system', 'content': GENERATE_SYSTEM_PROMPT},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.5,
        'max_tokens': 2000,
    }

    headers = {
        'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }

    resp = requests.post(settings.DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
    data = resp.json()

    if 'choices' not in data:
        raise Exception(f'DeepSeek API 调用失败: {data.get("error", {}).get("message", "未知错误")}')

    content = data['choices'][0]['message']['content'].strip()

    if content.startswith('```'):
        lines = content.split('\n')
        content = '\n'.join(line for line in lines if not line.startswith('```'))

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise Exception(f'DeepSeek 返回非JSON格式: {content[:200]}')


def review_answer(question_text: str, correct_answer: str, student_answer: str) -> dict:
    """批改学生的作答"""
    user_prompt = (
        f'【原题】\n{question_text}\n\n'
        f'【正确答案】\n{correct_answer}\n\n'
        f'【学生作答】\n{student_answer}'
    )
    return _call_deepseek(REVIEW_SYSTEM_PROMPT, user_prompt)
