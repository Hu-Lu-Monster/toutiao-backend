# FastAPI 头条项目后端

跟随课程逐步开发的 Python 后端学习项目，使用 FastAPI、SQLAlchemy 异步 ORM 和 MySQL。
目前包含新闻相关接口，以及用户注册、登录、令牌和用户信息功能，后续继续完善。

## 本地运行

当前开发环境为 Python 3.14、MySQL。先使用课程提供的建表 SQL 创建数据库和表。

在项目目录创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

复制配置示例：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，填写本地数据库连接信息，然后启动后端：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

接口文档地址：http://127.0.0.1:8000/docs

## 配置与版本记录

`.env` 保存本地数据库连接信息，不提交到 GitHub。`.env.example` 只提供示例值。
虚拟环境、Python 缓存和 PyCharm 本地设置已通过 `.gitignore` 排除。
GitHub 保存的是提交并推送的代码版本；MySQL 中的数据需要单独备份。
