# -
本仓库所有代码均为AI编写。在高中学习中，我认为最有效的学习方式就是编写错题本，所有我开发了一个软件通过OCR和大模型API调用来归类错题，同时定期复习错题
以下内容为AI编写：
# 智学笔记 — AI 智能错题本

> AI 驱动的智能错题分析与学情系统 | Django + DeepSeek + 百度 OCR

## 项目简介

智学笔记是一款面向高中生的智能错题管理学习系统。拍照上传错题后，系统自动完成 OCR 识别和 AI 分析，智能归因错误类型、评估难度等级，并基于艾宾浩斯遗忘曲线科学安排复习计划。支持 AI 实时批改作答、一键生成变式题（举一反三），搭配知识图谱可视化诊断薄弱环节。

## 核心功能

- **📸 智能导入** — 拍照上传 → OCR 识别 → AI 分析 → 自动归入错题本
- **🤖 AI 批改** — 学生重新作答后 AI 实时评分（百分制）+ 详细反馈
- **🔀 变式题生成** — 一键生成同知识点的四选一变式题，举一反三
- **📅 科学复习** — 基于艾宾浩斯遗忘曲线的间隔重复算法（1/3/7/14/30 天）
- **🗺️ 知识图谱** — 9 大学科 80+ 一级知识点，红/黄/绿三色掌握度诊断
- **📊 学习统计** — 掌握率、正确率、学科分布、错误类型等多维数据可视化
- **🦉 猫头鹰学伴** — XP 经验值 + 等级系统，学习游戏化

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 6.0 (Python) |
| 数据库 | SQLite3 |
| 前端 | HTML5 + CSS3 + 原生 JavaScript（响应式设计） |
| OCR 识别 | 百度智能云 OCR |
| AI 大模型 | DeepSeek |
| 复习算法 | 艾宾浩斯遗忘曲线 |

## 快速开始

### 1. 环境要求

- Python 3.10+
- 网络连接（用于调用 AI 和 OCR API）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

**方式一：环境变量（推荐）**

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY = "sk-你的密钥"
$env:BAIDU_OCR_API_KEY = "你的API Key"
$env:BAIDU_OCR_SECRET_KEY = "你的Secret Key"

# Linux / macOS
export DEEPSEEK_API_KEY="sk-你的密钥"
export BAIDU_OCR_API_KEY="你的API Key"
export BAIDU_OCR_SECRET_KEY="你的Secret Key"
```

**方式二：直接编辑 `cuotiben/settings.py`**

```python
DEEPSEEK_API_KEY = 'sk-你的密钥'
BAIDU_OCR_API_KEY = '你的API Key'
BAIDU_OCR_SECRET_KEY = '你的Secret Key'
```

> **获取 API 密钥：**
> - DeepSeek：https://platform.deepseek.com/ （新用户有免费额度）
> - 百度 OCR：https://cloud.baidu.com/ → 文字识别 → 创建应用（免费额度充足）

### 4. 初始化数据库

```bash
python manage.py migrate
```

### 5. 创建测试账号

```bash
python setup_users.py
```

脚本会自动创建三个测试账号（`student`、`teacher`、`admin`），密码随机生成并打印在终端。你也可以通过环境变量预设密码：

```bash
# Windows PowerShell
$env:STUDENT_PASSWORD = "我的密码"
$env:TEACHER_PASSWORD = "我的密码"
$env:ADMIN_PASSWORD = "我的密码"
```

### 6. 启动服务

**Windows 用户**：双击 `start_server.bat`

**手动启动**：

```bash
python manage.py runserver
```

浏览器访问 http://127.0.0.1:8000/

## 项目结构

```
├── manage.py              # Django 管理脚本
├── requirements.txt       # Python 依赖
├── setup_users.py         # 快速创建用户脚本
├── start_server.bat       # Windows 一键启动
├── cuotiben/              # Django 项目配置
│   ├── settings.py        #   核心配置（API Key 等）
│   └── urls.py            #   URL 路由
├── accounts/              # 用户账号模块（注册/登录）
├── errorbook/             # 错题本核心模块
│   ├── ai_agent.py        #   DeepSeek AI（分析/批改/出题）
│   ├── ocr.py             #   百度 OCR 图文识别
│   ├── knowledge_points.py#   知识图谱定义
│   ├── spaced_repetition.py#  艾宾浩斯遗忘曲线算法
│   ├── models.py          #   数据模型
│   ├── views.py           #   业务逻辑
│   └── templates/         #   前端页面模板
├── static/                # 静态资源（CSS/JS）
├── media/questions/       # 用户上传的错题图片
└── templates/             # 全局模板
```

## 使用说明

详细使用说明请参阅 [智学笔记-使用说明.md](../智学笔记-使用说明.md)

## 许可证

本项目仅用于学习交流目的。

---

*用 AI 技术真正赋能学习*
