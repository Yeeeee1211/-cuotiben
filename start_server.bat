@echo off
chcp 65001 >nul
echo ========================================
echo   AI 智能错题本 - 启动服务
echo ========================================
echo.

:: 检查依赖
pip install -r requirements.txt >nul 2>&1

:: 数据库迁移
echo [1/3] 执行数据库迁移...
python manage.py makemigrations accounts errorbook
python manage.py migrate

:: 创建测试账号
echo [2/3] 创建测试账号...
python setup_users.py

:: 启动服务
echo [3/3] 启动 Django 开发服务器...
echo.
echo 本地访问: http://localhost:8000
echo 测试账号由 setup_users.py 自动创建，密码随机生成（或通过环境变量指定）
echo.
echo 如需外网访问，使用 ngrok: ngrok http 8000
echo.
python manage.py runserver 0.0.0.0:8000

pause
