"""创建测试账号 — 密码从环境变量读取，未设置则使用随机密码"""
import os
import secrets
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cuotiben.settings')
django.setup()

from django.contrib.auth.models import User

users = [
    {'username': 'student', 'env': 'STUDENT_PASSWORD'},
    {'username': 'teacher', 'env': 'TEACHER_PASSWORD'},
    {'username': 'admin', 'env': 'ADMIN_PASSWORD'},
]

print('')
for u in users:
    password = os.environ.get(u['env']) or secrets.token_urlsafe(10)
    if User.objects.filter(username=u['username']).exists():
        print(f'  用户已存在: {u["username"]}')
        continue
    User.objects.create_user(username=u['username'], password=password)
    print(f'  已创建用户: {u["username"]}  /  {password}')
    if u['env'] not in os.environ:
        print(f'    (随机密码，可通过环境变量 {u["env"]} 指定)')

print('\n测试账号创建完成！')
