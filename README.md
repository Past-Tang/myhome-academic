<div align="center">
  <img src="assets/logo.svg" alt="MyHome Academic" width="680"/>

  # MyHome Academic

  **学术个人主页内容管理系统**

  [![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![Flask](https://img.shields.io/badge/Flask-Web-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
  [![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)](https://sqlite.org)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
</div>

---

## 项目概述

MyHome Academic 是一个基于 Flask 的学术个人主页内容管理系统（CMS）。提供完整的 RESTful API 后端，支持管理个人信息、教育背景、论文发表、研究项目、工作经历、荣誉奖项、友情链接等学术数据。内置用户认证系统（含图片验证码）、文件上传、Markdown 渲染等功能，首次启动自动初始化数据库并生成示例数据。

## 技术栈

- **Python**: 核心编程语言
- **Flask**: 轻量级 Web 框架，提供路由和会话管理
- **SQLite**: 嵌入式数据库，零配置持久化
- **Jinja2**: 服务端模板引擎
- **Pillow (PIL)**: 图片验证码生成
- **Markdown**: 内容 Markdown 渲染
- **HTML/CSS**: 前端页面（极简主题）

## 功能特性

- **完整 RESTful API** -- 8 个数据模块均提供 CRUD 接口（GET/POST/PUT/DELETE）
- **用户认证系统** -- SHA-256 密码哈希、Session 会话管理、`@login_required` 装饰器保护
- **图片验证码** -- 基于 Pillow 生成带干扰线和噪点的图片验证码，防止暴力破解
- **个人信息管理** -- 姓名、头衔、简介、头像、联系方式、社交链接（GitHub/LinkedIn/ORCID）
- **教育背景** -- 学位、院校、专业、年份、描述，支持标签和排序
- **论文发表** -- 标题、作者、期刊、年份、卷号、页码、DOI、摘要、关键词，区分期刊/会议类型
- **研究项目** -- 项目描述（支持 Markdown 详细描述）、角色、技术栈、GitHub 链接、状态标记
- **工作经历** -- 职位、机构、时间段、地点、描述
- **荣誉奖项** -- 奖项名称、颁发机构、年份、描述
- **友情链接** -- 名称、URL、描述、头像、激活状态控制
- **系统设置** -- 站点标题、描述、关键词、备案号、统计代码
- **文件上传** -- 支持图片和文档上传（PNG/JPG/GIF/PDF/DOC），自动时间戳命名
- **示例数据** -- 首次启动自动生成完整的示例数据（论文、项目、经历、奖项等）

## 安装说明

1. 克隆仓库到本地：
   ```bash
   git clone https://github.com/Past-Tang/myhome-academic.git
   cd myhome-academic
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 初始化管理员账户（可选，直接运行 `database.py`）：
   ```bash
   python database.py
   # 按提示输入管理员用户名和密码
   ```

4. 启动应用：
   ```bash
   python run.py
   ```

5. 访问 `http://localhost:5000` 查看学术主页

## 使用方法

1. 访问 `http://localhost:5000` 查看前台学术主页
2. 访问 `http://localhost:5000/admin` 进入后台管理界面
3. 使用管理员账户登录（需输入验证码）
4. 在后台管理各模块数据：个人信息、教育背景、论文、项目、经历、奖项、友链、设置
5. 修改保存后前台页面实时更新

## API 接口

所有 API 均以 `/api/` 为前缀，写操作需登录认证：

| 模块 | 端点 | 方法 | 说明 |
|:---|:---|:---|:---|
| 认证 | `/api/captcha` | GET | 获取图片验证码 |
| 认证 | `/api/login` | POST | 管理员登录 |
| 认证 | `/api/logout` | POST | 管理员登出 |
| 认证 | `/api/check-auth` | GET | 检查登录状态 |
| 个人信息 | `/api/profile` | GET/PUT | 获取/更新个人信息 |
| 教育背景 | `/api/education` | GET/POST | 列表/创建教育记录 |
| 教育背景 | `/api/education/<id>` | PUT/DELETE | 更新/删除教育记录 |
| 论文发表 | `/api/publications` | GET/POST | 列表/创建论文 |
| 论文发表 | `/api/publications/<id>` | PUT/DELETE | 更新/删除论文 |
| 研究项目 | `/api/projects` | GET/POST | 列表/创建项目 |
| 研究项目 | `/api/projects/<id>` | PUT/DELETE | 更新/删除项目 |
| 工作经历 | `/api/experience` | GET/POST | 列表/创建经历 |
| 工作经历 | `/api/experience/<id>` | PUT/DELETE | 更新/删除经历 |
| 荣誉奖项 | `/api/awards` | GET/POST | 列表/创建奖项 |
| 荣誉奖项 | `/api/awards/<id>` | PUT/DELETE | 更新/删除奖项 |
| 友情链接 | `/api/friends` | GET/POST | 列表/创建友链 |
| 友情链接 | `/api/friends/<id>` | PUT/DELETE | 更新/删除友链 |
| 系统设置 | `/api/settings` | GET/PUT | 获取/更新设置 |
| 文件上传 | `/api/upload` | POST | 上传文件 |

## 配置说明

| 配置项 | 位置 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `SECRET_KEY` | `app.py` | 环境变量或硬编码 | Flask 会话加密密钥 |
| `DATABASE_PATH` | `database.py` | `academic_homepage.db` | SQLite 数据库文件路径 |
| `DEBUG` | `app.py` | `True` | 调试模式（生产环境请关闭） |
| `HOST` | `app.py` | `0.0.0.0` | 监听地址 |
| `PORT` | `app.py` | `5000` | 监听端口 |

## 数据库结构

系统包含 8 张数据表：

| 表名 | 说明 | 关键字段 |
|:---|:---|:---|
| `users` | 管理员账户 | username, password_hash |
| `profile` | 个人信息（单条） | name, title, bio, research_interests |
| `education` | 教育背景 | degree, institution, field, year |
| `publications` | 论文发表 | title, authors, journal, doi, type |
| `projects` | 研究项目 | title, description, technologies, status |
| `experience` | 工作经历 | position, organization, location |
| `awards` | 荣誉奖项 | title, organization, year |
| `friends` | 友情链接 | name, url, is_active |
| `settings` | 系统设置 | site_title, beian, analytics_code |

## 项目结构

```
myhome-academic/
├── app.py               # Flask 主应用（路由、API、认证、验证码）
├── database.py          # 数据库初始化、表结构定义、示例数据生成
├── run.py               # 应用启动入口
├── requirements.txt     # Python 依赖列表
├── templates/
│   ├── index.html       # 前台学术主页模板
│   └── admin.html       # 后台管理界面模板
├── static/
│   ├── css/
│   │   └── minimal.css  # 极简主题样式
│   └── uploads/         # 文件上传目录（运行时生成）
├── academic_homepage.db # SQLite 数据库文件（运行时生成）
├── assets/
│   └── logo.svg         # 项目 Logo
├── LICENSE              # MIT 许可证
└── README.md
```

## 依赖项

| 包 | 用途 |
|:---|:---|
| Flask | Web 框架、路由、会话管理 |
| Pillow | 图片验证码生成 |
| markdown | Markdown 内容渲染 |
| sqlite3 | 数据库（Python 内置） |

## 自定义主题

修改 `static/css/minimal.css` 可自定义页面样式：
- **配色方案** -- 修改 CSS 变量或直接修改颜色值
- **字体选择** -- 更换 `font-family` 属性
- **布局间距** -- 调整 `margin`、`padding` 值
- **卡片样式** -- 修改 `border-radius`、`box-shadow` 等

## 常见问题

### 数据库文件在哪里？
默认为项目根目录下的 `academic_homepage.db`，可在 `database.py` 中修改 `DATABASE_PATH`。

### 如何重置数据？
删除 `academic_homepage.db` 文件后重启应用，系统会自动重新初始化并生成示例数据。

### 如何备份数据？
直接复制 `academic_homepage.db` 文件即可完成完整备份。

### 验证码图片不显示？
确保已安装 Pillow 库：`pip install Pillow`。如未安装，系统会自动降级为文本验证码。

### 如何部署到服务器？
推荐使用 Gunicorn + Nginx：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
生产环境请务必：
- 修改 `SECRET_KEY` 为随机强密码
- 关闭 `DEBUG` 模式
- 配置 HTTPS

## 许可证

[MIT License](LICENSE)

## 免责声明

本项目仅供学习参考使用。示例数据中的人物信息均为虚构，不代表任何真实个人。