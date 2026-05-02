import time
import base64
import requests
from django.conf import settings

_access_token = None
_token_expires_at = 0


def _get_access_token():
    """获取百度OCR access_token，缓存25天"""
    global _access_token, _token_expires_at
    if _access_token and time.time() < _token_expires_at:
        return _access_token

    if not settings.BAIDU_OCR_API_KEY or not settings.BAIDU_OCR_SECRET_KEY:
        return None

    resp = requests.post(settings.BAIDU_OCR_ACCESS_TOKEN_URL, params={
        'grant_type': 'client_credentials',
        'client_id': settings.BAIDU_OCR_API_KEY,
        'client_secret': settings.BAIDU_OCR_SECRET_KEY,
    }, timeout=10)
    data = resp.json()
    if 'access_token' in data:
        _access_token = data['access_token']
        _token_expires_at = time.time() + 25 * 24 * 3600
        return _access_token
    return None


def recognize_text(image_path: str) -> str:
    """调用百度OCR accurate_basic 识别图片中的文字"""
    token = _get_access_token()
    if not token:
        raise Exception('百度OCR access_token 获取失败，请检查 API Key')

    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    resp = requests.post(settings.BAIDU_OCR_URL, params={'access_token': token}, data={
        'image': image_data,
    }, timeout=30)
    result = resp.json()

    if 'words_result' in result:
        texts = [item['words'] for item in result['words_result']]
        return '\n'.join(texts)
    elif 'error_code' in result:
        raise Exception(f'百度OCR识别失败: {result.get("error_msg", "未知错误")}')
    else:
        raise Exception('百度OCR识别失败: 未知响应格式')
