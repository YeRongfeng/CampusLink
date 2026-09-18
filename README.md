# CampusLink

校园生活 Web 应用公共框架，提供注册登录、个人资料、图片上传和统一页面布局。校园拼车、校园悬赏、二手书由各模块负责人接续开发，目前仅保留入口和占位页。

技术栈：Vue 3 + TypeScript + Naive UI + Tailwind CSS / FastAPI + SQLAlchemy / MySQL。

## Quick Start

环境：Node.js 22.12+、Python 3.12、MySQL 8。以下命令使用 Windows PowerShell，从项目根目录开始。

### 1. 安装依赖

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

### 2. 配置数据库

本机 MySQL 服务启动后，执行：

```powershell
backend/.venv/Scripts/python.exe database/setup.py
```

在终端输入 MySQL 管理账号密码，脚本自动执行建库建表 SQL、创建项目专用账号，并生成 `backend/.env` 和随机 JWT 密钥，无需复制或编辑文件。默认使用本机 3306 端口和 root 管理账号；其他配置可用 `--host`、`--port`、`--user` 指定。

已有 `.env` 时只检查连接和用户表，不覆盖配置或数据。

> 如果这台电脑使用项目附带的本地 MySQL，先运行 `backend/.venv/Scripts/python.exe database/local_mysql.py start`。其他电脑使用自己已安装的 MySQL 服务即可。

### 3. 启动

终端一，启动后端：

```powershell
cd backend
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

终端二，从项目根目录启动前端：

```powershell
cd frontend
npm run dev
```

- 网页：http://127.0.0.1:5173
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

前端开发服务器已将 `/api`、`/uploads` 代理到后端；需要改后端地址时参照 `frontend/.env.example`。

### 4. 开发账号（可选）

在 `backend` 目录执行：

```powershell
.venv/Scripts/python.exe -m app.seed
```

创建 `user01`、`user02`、`user03`，密码均为 `CampusLink123!`，已有账号不覆盖。

## 开发与交接

- [项目文档](docs/README.md)：需求、数据库与程序设计、测试报告、部署维护、用户手册和工作分配。
- 前端构建检查：在 `frontend` 目录运行 `npm run build`。
- 不提交真实 `.env`、`.local/`、虚拟环境、`node_modules/`、上传文件或构建产物。
