"""SVG icon set — clean, scalable icons replacing emoji"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_ICONS = {
    'logo': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="3" y="2" width="18" height="20" rx="2" fill="#4285f4"/><rect x="6" y="5" width="12" height="3" rx="1" fill="#fff" opacity=".9"/><rect x="6" y="10" width="9" height="1.5" rx=".75" fill="#fff" opacity=".5"/><rect x="6" y="13" width="10" height="1.5" rx=".75" fill="#fff" opacity=".5"/><rect x="6" y="16" width="7" height="1.5" rx=".75" fill="#fff" opacity=".5"/></svg>',

    'camera': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="13" r="4" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'pencil': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M17 3a2.83 2.83 0 014 4L7.5 20.5 2 22l1.5-5.5z" stroke="currentColor" stroke-width="2" fill="none"/><line x1="15" y1="5" x2="19" y2="9" stroke="currentColor" stroke-width="2"/></svg>',

    'clipboard': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2" stroke="currentColor" stroke-width="2" fill="none"/><rect x="8" y="2" width="8" height="4" rx="1" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'chart': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="3" y="12" width="4" height="9" rx="1" fill="#fbbc04"/><rect x="9" y="7" width="4" height="14" rx="1" fill="#34a853"/><rect x="15" y="3" width="4" height="18" rx="1" fill="#4285f4"/></svg>',

    'check': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#34a853"/><path d="M8 12l3 3 5-5" stroke="#fff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',

    'cross': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#ea4335"/><path d="M15 9l-6 6M9 9l6 6" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>',

    'document': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'book': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M4 19.5A2.5 2.5 0 016.5 17H20" stroke="currentColor" stroke-width="2" fill="none"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'book_open': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z" stroke="currentColor" stroke-width="2" fill="none"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'pin': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 2v10l4 4H8l4-4V2z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="2" r="1.5" fill="currentColor"/></svg>',

    'rocket': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z" stroke="currentColor" stroke-width="2" fill="none"/><path d="M12 15l-3-3a22 22 0 012.89-2.89L9.84 7.16c3.6-2.17 8.12-1.74 11.15.63l-2.54 2.54M12 15l3-3" stroke="currentColor" stroke-width="2" fill="none"/><path d="M16.5 5.5a2 2 0 012 2" stroke="currentColor" stroke-width="2"/></svg>',

    'arrow_left': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',

    'arrow_right': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',

    'upload': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="17 8 12 3 7 8" stroke="currentColor" stroke-width="2" fill="none"/><line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2"/></svg>',

    'refresh': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" stroke-width="2" fill="none"/><path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'warning': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="#e65100" stroke-width="2" fill="none"/><line x1="12" y1="9" x2="12" y2="13" stroke="#e65100" stroke-width="2"/><circle cx="12" cy="17" r="1" fill="#e65100"/></svg>',

    'folder': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'smile': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#34a853"/><circle cx="8.5" cy="9" r="1.2" fill="#fff"/><circle cx="15.5" cy="9" r="1.2" fill="#fff"/><path d="M8 14c1.5 2 6.5 2 8 0" stroke="#fff" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>',

    'target': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="6" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="2" fill="currentColor"/></svg>',

    'save': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="17 21 17 13 7 13 7 21" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="7 3 7 8 15 8" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'dice': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="2" y="2" width="20" height="20" rx="3" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="8" cy="8" r="1.5" fill="currentColor"/><circle cx="16" cy="16" r="1.5" fill="currentColor"/></svg>',

    'delete': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke="currentColor" stroke-width="2" fill="none"/></svg>',

    'star': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" stroke="#fbbc04" stroke-width="1.5" fill="#fbbc04" opacity=".3"/></svg>',

    'search': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/><line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" stroke-width="2"/></svg>',

    'loading': '<svg width="40" height="40" viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="16" stroke="#e0e0e0" stroke-width="4"/><path d="M20 4a16 16 0 0116 16" stroke="#4285f4" stroke-width="4" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 20 20" to="360 20 20" dur="0.8s" repeatCount="indefinite"/></path></svg>',

    'spinner': '<svg width="32" height="32" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="12" stroke="#e0e0e0" stroke-width="3"/><path d="M16 4a12 12 0 0112 12" stroke="#4285f4" stroke-width="3" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 16 16" to="360 16 16" dur="0.8s" repeatCount="indefinite"/></path></svg>',

    'happy_owl': '<svg width="40" height="40" viewBox="0 0 40 40" fill="none"><ellipse cx="20" cy="22" rx="16" ry="14" fill="#fbbc04"/><ellipse cx="20" cy="12" rx="13" ry="10" fill="#f9a825"/><polygon points="20,2 15,16 25,16" fill="#fbbc04"/><polygon points="20,4 16,16 24,16" fill="#f9a825"/><circle cx="15" cy="16" r="5" fill="#fff"/><circle cx="25" cy="16" r="5" fill="#fff"/><circle cx="15.5" cy="15.5" r="2.5" fill="#333"/><circle cx="25.5" cy="15.5" r="2.5" fill="#333"/><circle cx="16.5" cy="14.5" r="1" fill="#fff"/><circle cx="26.5" cy="14.5" r="1" fill="#fff"/><path d="M18 20 Q20 23 22 20" stroke="#333" stroke-width="1.5" fill="none" stroke-linecap="round"/><circle cx="20" cy="32" r="1.5" fill="#f9a825"/><rect x="18.5" y="33" width="3" height="3" rx="1" fill="#f9a825"/></svg>',

    'sad_owl': '<svg width="40" height="40" viewBox="0 0 40 40" fill="none"><ellipse cx="20" cy="22" rx="16" ry="14" fill="#bdbdbd"/><ellipse cx="20" cy="12" rx="13" ry="10" fill="#9e9e9e"/><polygon points="20,2 15,16 25,16" fill="#bdbdbd"/><polygon points="20,4 16,16 24,16" fill="#9e9e9e"/><circle cx="15" cy="16" r="5" fill="#fff"/><circle cx="25" cy="16" r="5" fill="#fff"/><circle cx="15.5" cy="15.5" r="2.5" fill="#757575"/><circle cx="25.5" cy="15.5" r="2.5" fill="#757575"/><path d="M18 21 Q20 18 22 21" stroke="#757575" stroke-width="1.5" fill="none" stroke-linecap="round"/><circle cx="11" cy="30" r="1.2" fill="#64b5f6"/><path d="M11 31.5 L11 34" stroke="#64b5f6" stroke-width="0.8"/></svg>',
}


@register.simple_tag
def svg_icon(name):
    return mark_safe(_ICONS.get(name, ''))


@register.simple_tag
def icon(name):
    return mark_safe(f'<span style="display:inline-flex;align-items:center;gap:4px">{_ICONS.get(name, "")}</span>')


@register.inclusion_tag('errorbook/_owl_pet.html', takes_context=True)
def owl_pet(context):
    request = context['request']
    if not request.user.is_authenticated:
        return {'xp': 0, 'level': 1, 'xp_pct': 0, 'mood': 'sad'}

    from errorbook.models import Question, ReviewRecord
    from django.utils import timezone

    total_q = Question.objects.filter(user=request.user).count()
    total_r = ReviewRecord.objects.filter(user=request.user).count()
    correct_r = ReviewRecord.objects.filter(user=request.user, is_correct=True).count()

    xp = total_q * 10 + total_r * 5 + correct_r * 10
    level = xp // 100 + 1
    xp_pct = round(xp % 100)

    today = timezone.localtime().date()
    today_reviews = ReviewRecord.objects.filter(
        user=request.user,
        reviewed_at__date=today
    ).exists()
    mood = 'happy' if today_reviews else 'sad'

    return {'xp': xp, 'level': level, 'xp_pct': xp_pct, 'mood': mood}
