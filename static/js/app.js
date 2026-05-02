/* === 智学笔记 — SPA 路由 + 交互 === */

(function () {
    'use strict';

    // 仅在 SPA shell 页面运行
    var contentArea = document.getElementById('content-area');
    if (!contentArea) return;

    var sidebar = document.getElementById('sidebar');
    var hamburger = document.getElementById('hamburger');
    var overlay = document.getElementById('sidebar-overlay');
    var tools = document.querySelectorAll('.sidebar-tool[data-route]');
    var currentRoute = window.location.pathname;

    // 初始化侧边栏活跃状态
    function updateActiveTool(url) {
        tools.forEach(function (t) {
            var route = t.getAttribute('data-route');
            t.classList.toggle('active', url === route || (route !== '/errorbook/' && url.startsWith(route)));
        });
    }
    updateActiveTool(currentRoute);

    // === SPA 导航 ===
    function navigate(url, push) {
        if (push === undefined) push = true;
        currentRoute = url;
        updateActiveTool(url);

        // 加载中
        contentArea.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;padding:60px"><div class="spinner"></div></div>';

        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function (res) {
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.text();
            })
            .then(function (html) {
                // 检测响应是否为完整 SPA 页面（含 app-layout）→ 提取内容区
                var temp = document.createElement('div');
                temp.innerHTML = html;
                var innerContent = temp.querySelector('.content-area');
                if (innerContent) {
                    contentArea.innerHTML = innerContent.innerHTML;
                } else {
                    contentArea.innerHTML = html;
                }
                contentArea.scrollTop = 0;
                initContentScripts();
            })
            .catch(function (err) {
                contentArea.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><p>加载失败：' + err.message + '</p></div>';
            });

        if (push) {
            history.pushState({ route: url }, '', url);
        }
    }

    // 侧边栏点击
    tools.forEach(function (tool) {
        tool.addEventListener('click', function () {
            var route = this.getAttribute('data-route');
            if (route && route !== currentRoute) {
                navigate(route);
            }
            closeSidebar();
        });
    });

    // 浏览器前进/后退
    window.addEventListener('popstate', function (e) {
        if (e.state && e.state.route) {
            navigate(e.state.route, false);
        } else {
            navigate(window.location.pathname, false);
        }
    });

    // 拦截内容区内的链接（相对路径）转为 SPA 导航
    contentArea.addEventListener('click', function (e) {
        var link = e.target.closest('a');
        if (!link) return;
        var href = link.getAttribute('href');
        if (!href) return;
        // 跳过外部链接、锚点、logout、admin
        if (href.startsWith('http') || href.startsWith('#') ||
            href.indexOf('logout') >= 0 || href.startsWith('/admin')) return;
        // 跳过明确标注不拦截的链接
        if (link.hasAttribute('data-no-spa')) return;
        // 跳过表单提交页面（如 review check, delete）
        if (link.hasAttribute('data-method')) return;

        e.preventDefault();
        navigate(href, true);
    });

    // 拦截内容区内的表单提交（GET 表单）
    contentArea.addEventListener('submit', function (e) {
        var form = e.target.closest('form');
        if (!form) return;
        // 跳过 POST 表单
        if (form.method.toUpperCase() === 'POST') return;
        // 跳过有 data-no-spa 的表单
        if (form.hasAttribute('data-no-spa')) return;

        e.preventDefault();
        var formData = new FormData(form);
        var params = new URLSearchParams(formData).toString();
        var url = form.action || window.location.pathname;
        navigate(url + (params ? '?' + params : ''), true);
    });

    // === 汉堡菜单 ===
    function openSidebar() {
        sidebar.classList.add('open');
        overlay.classList.add('show');
        hamburger.classList.add('open');
    }
    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
        hamburger.classList.remove('open');
    }

    if (hamburger) {
        hamburger.addEventListener('click', function () {
            sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
        });
    }
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // === 内容区脚本初始化 ===

    function initContentScripts() {
        // 知识图谱标签点击 → 筛选跳转
        var kpTags = contentArea.querySelectorAll('.kp-tag[data-subject][data-kp]');
        kpTags.forEach(function (tag) {
            tag.addEventListener('click', function () {
                var subject = this.getAttribute('data-subject');
                var kp = this.getAttribute('data-kp');
                var url = '/errorbook/questions/?subject=' + encodeURIComponent(subject) +
                          '&kp=' + encodeURIComponent(kp);
                navigate(url, true);
            });
        });

        // 复习随机出题按钮
        var randomBtn = contentArea.querySelector('#random-question-btn');
        if (randomBtn) {
            randomBtn.addEventListener('click', function () {
                var subject = this.getAttribute('data-subject') || '';
                fetch('/errorbook/api/random/' + (subject ? '?subject=' + encodeURIComponent(subject) : ''))
                    .then(function (res) { return res.json(); })
                    .then(function (data) {
                        if (data.id) {
                            window.location.href = '/errorbook/review/' + data.id + '/';
                        } else {
                            alert('暂无错题');
                        }
                    });
            });
        }

        // 导入页面图片上传 — 点击区域触发选择 + 预览显示
        var imgInput = contentArea.querySelector('#image-input');
        var previewImg = contentArea.querySelector('#preview-img');
        var dropZone = contentArea.querySelector('#drop-zone');
        var previewContainer = contentArea.querySelector('#preview-container');
        if (imgInput) {
            // 点击上传区域触发文件选择（兜底，label for 属性本身也可触发）
            if (dropZone) {
                dropZone.addEventListener('click', function (e) {
                    if (e.target !== imgInput) { imgInput.click(); }
                });
            }
            // 文件选择后显示预览
            imgInput.addEventListener('change', function () {
                var file = this.files[0];
                if (file) {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        if (previewImg) previewImg.src = e.target.result;
                        if (previewContainer) previewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            });
        }

        // 举一反三生成按钮
        var genBtn = contentArea.querySelector('#generate-similar-btn');
        if (genBtn) {
            genBtn.addEventListener('click', function () {
                var qid = this.getAttribute('data-qid');
                var container = contentArea.querySelector('#similar-container');
                container.innerHTML = '<div class="spinner"></div><p style="text-align:center;color:var(--text-muted);margin-top:8px">AI 正在生成变式题...</p>';
                fetch('/errorbook/api/generate-question/' + qid + '/')
                    .then(function (res) { return res.json(); })
                    .then(function (data) {
                        if (data.error) { container.innerHTML = '<p style="color:var(--danger)">' + data.error + '</p>'; return; }
                        var html = '<div class="similar-question">' + data.question + '</div>';
                        html += '<div class="option-list">';
                        var keys = Object.keys(data.options);
                        keys.forEach(function (k) {
                            html += '<div class="option-item" data-opt="' + k + '">' + k + '. ' + data.options[k] + '</div>';
                        });
                        html += '</div>';
                        html += '<button class="btn btn-outline" id="reveal-answer-btn" style="margin-top:12px">显示答案</button>';
                        html += '<div id="answer-panel" style="display:none;margin-top:12px">';
                        html += '<p style="font-weight:600;color:var(--success)">正确答案：' + data.correct_option + '</p>';
                        html += '<div class="explanation-box">' + data.explanation + '</div>';
                        html += '</div>';
                        container.innerHTML = html;

                        // 选项点击
                        container.querySelectorAll('.option-item').forEach(function (opt) {
                            opt.addEventListener('click', function () {
                                container.querySelectorAll('.option-item').forEach(function (o) { o.classList.remove('selected'); });
                                this.classList.add('selected');
                            });
                        });
                        // 显示答案
                        container.querySelector('#reveal-answer-btn').addEventListener('click', function () {
                            var panel = container.querySelector('#answer-panel');
                            panel.style.display = 'block';
                            this.style.display = 'none';
                            var correct = data.correct_option;
                            container.querySelectorAll('.option-item').forEach(function (o) {
                                var opt = o.getAttribute('data-opt');
                                if (opt === correct) o.classList.add('correct-opt');
                                if (o.classList.contains('selected') && opt !== correct) o.classList.add('wrong-opt');
                            });
                        });
                    })
                    .catch(function (err) {
                        container.innerHTML = '<p style="color:var(--danger)">请求失败：' + err.message + '</p>';
                    });
            });
        }
    }

    initContentScripts();
})();
