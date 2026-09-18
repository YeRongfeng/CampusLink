# CampusLink Framework V1.0

## Codex 开发规格书草案

### 0. 开发目标

本阶段只完成 **CampusLink 的公共开发框架**，目标是：

> 为“校园拼车 / CampusQuest 校园悬赏 / 二手书”三个独立功能提供统一、可运行、视觉一致、易于扩展的 Web 开发基础。

本阶段**不是**开发三个业务功能。

最终状态应该是：

```text
CampusLink 可以完整启动
        ↓
注册 / 登录可用
        ↓
首页和个人中心可用
        ↓
三个业务模块都有入口
        ↓
Ride / Quest / Book 各自拥有独立开发空间
        ↓
三名开发者可以直接开始业务开发
```

---

# 1. 技术栈冻结

这一版先锁定：

```text
Frontend
Vue 3
Vite
TypeScript
Vue Router
Pinia
Axios
Naive UI
Tailwind CSS

Backend
Python
FastAPI
SQLAlchemy
Pydantic

Authentication
JWT

Database
MySQL

File Storage
Local filesystem

Version Control
Git
```

原则：

> **Naive UI 负责组件统一，Tailwind 负责布局。**

不要大量手写 CSS，也不要再引入第二套 UI 组件库。

---

# 2. Codex 第一阶段：初始化整个工程

先只完成工程骨架。

目标目录：

```text
CampusLink/
│
├── frontend/
│
├── backend/
│
├── database/
│
├── docs/
│
├── README.md
└── .gitignore
```

前端完成：

```text
Vue 3 + Vite + TypeScript
Vue Router
Pinia
Axios
Naive UI
Tailwind CSS
```

后端完成：

```text
FastAPI
SQLAlchemy
Pydantic
MySQL 驱动
JWT 相关依赖
```

这个阶段先要求：

```text
frontend 能运行
backend 能运行
frontend 能访问 backend
backend 能连接 MySQL
```

例如访问：

```text
GET /api/health
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

### 第一阶段验收

只验证：

```text
npm install
npm run dev

以及

pip install -r requirements.txt
uvicorn app.main:app --reload
```

都能正常运行。

**此时不要继续写业务。**

---

# 3. Codex 第二阶段：建立公共代码结构

前端建议形成：

```text
frontend/src/
│
├── api/
│   ├── request.ts
│   ├── auth.ts
│   ├── user.ts
│   └── file.ts
│
├── components/
│   ├── common/
│   └── layout/
│
├── views/
│   ├── Home/
│   ├── Login/
│   ├── Register/
│   ├── Profile/
│   ├── Ride/
│   ├── Quest/
│   └── Book/
│
├── router/
├── stores/
├── types/
├── utils/
│
├── App.vue
└── main.ts
```

后端：

```text
backend/app/
│
├── main.py
│
├── common/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── response.py
│   └── exceptions.py
│
├── auth/
│   ├── router.py
│   ├── schemas.py
│   └── service.py
│
├── user/
│   ├── router.py
│   ├── models.py
│   ├── schemas.py
│   └── service.py
│
└── modules/
    ├── ride/
    ├── quest/
    └── book/
```

这里 Ride / Quest / Book 暂时只建立目录。

甚至可以只有：

```text
router.py
README.md
```

用来告诉后续开发者：

> 这是你的模块。

---

# 4. 第三阶段：公共用户系统

这是 Framework V1 最核心的功能之一。

第一版 User 保持简单：

```text
user
────────────────────
id
username
password_hash
nickname
avatar
created_at
updated_at
```

暂时不要加入：

```text
积分
信誉
学生认证
交易次数
拼车评分
```

因为这些都属于后续扩展。

---

## 必须实现的用户功能

```text
注册
登录
退出
获取当前用户
修改基本资料
```

对应 API：

```text
POST /api/auth/register

POST /api/auth/login

GET /api/users/me

PUT /api/users/me
```

---

# 5. 登录认证

采用 JWT。

流程固定：

```text
用户名 + 密码
      ↓
/api/auth/login
      ↓
验证密码
      ↓
生成 JWT
      ↓
前端保存 Token
      ↓
Axios 自动添加 Authorization
      ↓
后端解析当前用户
```

统一请求头：

```text
Authorization: Bearer <token>
```

前端 Pinia 只保存：

```text
token
currentUser
isAuthenticated
```

不要把三个业务的数据塞进公共 Store。

---

# 6. 第四阶段：统一 API 基础设施

这个对后面的三个同学很重要。

前端统一通过：

```text
src/api/request.ts
```

访问后端。

它应该负责：

```text
baseURL
Authorization
请求超时
401 处理
通用错误处理
```

以后业务同学不要直接：

```text
axios.get(...)
```

而统一：

```text
request.get(...)
```

---

# 7. 后端统一响应格式

所有接口必须统一。

成功：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 400,
  "message": "具体错误",
  "data": null
}
```

后续分页统一：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20
  }
}
```

即使 V1 暂时没分页业务，也最好提前定义好。

---

# 8. 第五阶段：统一视觉框架

这一步关系到最后三个模块会不会看起来像三个网站。

公共框架应该先确定：

```text
页面背景
内容最大宽度
顶部导航栏
全局间距
圆角
卡片风格
字体层级
主色
按钮风格
```

但是不要搞很复杂的“设计系统”。

我建议产品视觉定位：

> **简洁、年轻、校园生活类，而不是管理后台。**

首页大致：

```text
┌──────────────────────────────────────┐
│ CampusLink                           │
│ 首页   拼车   校园悬赏   二手书   👤 │
├──────────────────────────────────────┤
│                                      │
│       连接校园中的人与需要            │
│                                      │
│  ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ 🚗     │ │ 📌     │ │ 📚     │   │
│  │校园拼车│ │校园悬赏│ │二手书  │   │
│  └────────┘ └────────┘ └────────┘   │
│                                      │
└──────────────────────────────────────┘
```

建议同时保证：

```text
Desktop
Tablet
Mobile
```

至少基础响应式正常。

---

# 9. 建议增加一份统一 Design Token

这个对多人开发很有帮助。

例如统一定义：

```text
页面最大宽度
1200px

主要圆角
12px

卡片间距
16 / 24px

页面间距
24 / 32px
```

颜色不建议让三个人自己随便选。

公共框架统一提供：

```text
primary
success
warning
error

background
surface
text-primary
text-secondary
border
```

以后三个人只使用这些既有颜色体系。

---

# 10. 第六阶段：统一 Layout

公共组件至少包含：

```text
AppHeader
AppContainer
ModuleCard
EmptyState
PageHeader
UserAvatar
```

注意不要提前造很多“万能组件”。

公共组件只做：

> **三个模块大概率都会使用的东西。**

比如：

`PageHeader`：

```text
校园拼车

找到与你路线相近的同学
                        [发布]
```

未来 Ride / Quest / Book 都可以使用。

---

# 11. 第七阶段：首页

首页要完成，但不需要做复杂 Feed。

建议包含：

```text
Hero 区域
三个业务模块入口
简单平台介绍
当前用户信息
```

例如：

> CampusLink
> 连接校园中的人与需要

三个模块：

```text
🚗 校园拼车
找到与你同行的人

📌 CampusQuest
让顺手的人帮你解决小事

📚 二手书
让闲置教材继续流转
```

点击分别进入：

```text
/ride
/quest
/book
```

---

# 12. 第八阶段：三个模块占位页

这是 Framework V1 很重要的边界。

例如 Ride：

```text
校园拼车
──────────────────

寻找时间与路线相近的同学。

[功能正在开发]
```

Quest：

```text
CampusQuest 校园悬赏
──────────────────

发布校园互助需求，让顺路或擅长的人帮你完成。

[功能正在开发]
```

Book：

```text
校园二手书
──────────────────

让闲置教材和参考书继续流转。

[功能正在开发]
```

**到此为止。**

Codex 不允许继续生成：

```text
拼车发布
悬赏领取
图书交易
```

---

# 13. 第九阶段：个人中心

公共 Profile 第一版只负责：

```text
头像
用户名
昵称
修改资料
```

然后预留：

```text
我的拼车
我的悬赏
我的书籍
```

例如：

```text
/profile

我的 CampusLink
────────────────────
头像

张三
zhangsan

[编辑资料]

我的内容
🚗 我的拼车
📌 我的悬赏
📚 我的书籍
```

这些入口可以暂时进入：

```text
/ride/mine
/quest/mine
/book/mine
```

对应页面仍然是占位页。

---

# 14. 第十阶段：基础文件上传

这个可以作为 Framework V1 的最后一个公共能力。

统一 API：

```text
POST /api/files/upload
```

用于：

```text
头像
书籍照片
悬赏图片
```

存储：

```text
backend/uploads/
```

数据库只保存 URL。

不要搞对象存储。

---

# 15. 数据库初始化

必须建立：

```text
database/init.sql
```

Framework V1 第一版只真正定义：

```sql
CREATE DATABASE ...

CREATE TABLE user (...)
```

同时预留：

```sql
-- Ride Module

-- Quest Module

-- Book Module
```

业务同学后续自行补充。

---

# 16. 开发环境配置

后端配置不要直接写死：

```text
localhost
root
password
```

建议提供：

```text
.env.example
```

例如：

```text
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=campuslink
DATABASE_USER=root
DATABASE_PASSWORD=your_password

JWT_SECRET=change_me
```

真正的 `.env` 不提交 Git。

这个最好 Framework V1 就规范下来。

---

# 17. README 是 Framework V1 的正式组成部分

不是最后再随便写。

至少必须包含：

```text
项目简介

技术栈

目录结构

环境要求

数据库初始化

启动后端

启动前端

测试账号

API 文档地址

三个模块负责人如何开发
```

目标：

> 一个完全没参与搭框架的同学，拿到仓库后能自己跑起来。

---

# 18. 建议增加测试数据

初始化时可以提供：

```text
user01
user02
user03
```

密码统一例如开发阶段：

```text
123456
```

当然数据库里存哈希。

这样后面测试：

```text
user01 发布
user02 加入
user03 查看
```

会方便很多。

---

# 19. Codex 必须编写基础测试

我建议不要完全裸奔。

至少后端验证：

```text
注册正常
重复用户名失败
正确密码登录成功
错误密码登录失败
未登录访问 /users/me 返回 401
登录后能获取自己的资料
```

前端不用第一阶段搞复杂自动化 E2E。

但至少 Codex 自己完成：

```text
npm build
```

保证 TypeScript 没有错误。

---

# 20. Framework V1 明确禁止范围

这段以后可以原样放进 Codex Prompt：

> 在未收到明确指令前，不得实现以下内容：

```text
校园拼车业务逻辑
CampusQuest 业务逻辑
二手书业务逻辑

即时聊天
WebSocket
支付
积分体系
评价体系
复杂权限
后台管理系统
地图导航
第三方登录
AI 功能
Redis
Celery
消息队列
微服务
Docker/Kubernetes
```

这样避免 Codex：

> “为了让项目更完整，我顺手又做了……”

最后框架失控。

---

# 21. 三个模块的开发约束

Framework V1 做完之后给三个同学的约束应该很简单：

```text
Ride:
frontend/src/views/Ride
backend/app/modules/ride
/api/rides/**

Quest:
frontend/src/views/Quest
backend/app/modules/quest
/api/quests/**

Book:
frontend/src/views/Book
backend/app/modules/book
/api/books/**
```

同时：

> 如果需要修改公共 User、认证、Layout、公共请求工具，必须先沟通。

这样你最后合并的风险会小很多。

---

# 22. Framework V1 最终验收测试

最后你自己只需要按照一个真实用户流程检查：

```text
第一次打开 CampusLink

↓
进入注册页面

↓
注册 user01

↓
自动/手动登录

↓
进入首页

↓
顶部显示当前用户

↓
点击校园拼车

↓
进入 Ride 占位页

↓
点击 CampusQuest

↓
进入 Quest 占位页

↓
点击二手书

↓
进入 Book 占位页

↓
进入个人中心

↓
修改昵称 / 头像

↓
退出

↓
重新登录成功
```

同时技术层面：

```text
MySQL 能通过 init.sql 初始化

FastAPI /docs 可正常访问

npm run build 成功

README 可以从零启动项目
```

只要这些全部成立：

# Framework V1 完成。

---

# 23. 我建议 Codex 不要一次完成全部，而是分 4 轮

这是我目前比较推荐的实际操作方式。

```text
Round 1
项目初始化
+
前后端连通
+
数据库

↓

Round 2
用户系统
+
JWT
+
公共 API

↓

Round 3
视觉框架
+
首页
+
导航
+
个人中心
+
三个业务插槽

↓

Round 4
文件上传
+
README
+
基础测试
+
清理和验收
```

每完成一轮，你自己先运行、看看页面、检查目录。

没问题再继续。

**不要第一条 prompt 就叫 Codex 把整个项目全部生成。**

因为这样最容易出现：

> 项目能跑，但架构已经和我们规划的不一样了。

---

# 24. 所以我们现在实际上已经到了可以让 Codex 开工的位置

完整流程已经从：

```text
选题
  ↓
确定三个模块
  ↓
定义 CampusLink
  ↓
设计公共/业务边界
  ↓
选择技术栈
  ↓
定义 Framework V1
  ↓
拆分 Codex 开发任务
```
