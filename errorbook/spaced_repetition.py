"""艾宾浩斯遗忘曲线 — 间隔重复算法"""
INTERVALS = [1, 3, 7, 14, 30]


def parse_score(ai_score_str):
    """'85/100' → 85; 失败返回 None"""
    try:
        return int(ai_score_str.split('/')[0])
    except (ValueError, IndexError, AttributeError):
        return None


def compute_next_review(score_int, current_review_count):
    """
    score_int: 0-100 整数
    current_review_count: 本次复习前的 review_count
    返回: (new_review_count, interval_days)
    """
    if score_int >= 80:
        new_count = current_review_count + 1
        idx = min(new_count, len(INTERVALS) - 1)
        return new_count, INTERVALS[idx]
    elif score_int < 60:
        return 0, 1
    else:
        idx = min(current_review_count, len(INTERVALS) - 1)
        return current_review_count, INTERVALS[idx]
