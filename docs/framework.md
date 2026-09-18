# CampusLink 公共框架设计与开发思路

## 1. 工作职责与目标

本部分对应小组分工“负责按要求给出一套可供三个功能开发的程序总框架及提出思路”。在小组已经确定选题与技术方案的基础上，搭建可运行、可复用、便于协作的公共工程，为校园拼车、校园悬赏和二手书三个相对独立的功能提供开发基础。

具体负责工程初始化、前后端与数据库连通、公共用户系统、认证与请求处理、首页与公共布局、个人中心、图片上传，以及启动和接入说明。三个业务模块的需求细化、页面流程、数据表和业务接口由各模块负责人自行设计实现。

课程要求提交完整 Web 应用及相关文档。本文件说明公共框架的设计和交接，不代替三个业务模块的详细设计，也不代表全组项目已全部完成。

## 2. 总体设计思路

采用前后端分离、后端单体分模块的结构。三个功能共用一个用户系统、一套页面布局和一个数据库，通过独立目录和接口前缀划分开发范围，减少重复开发及合并冲突。

```text
浏览器：Vue 页面、公共组件、登录状态
                    ↓
统一请求工具：Token、超时、错误处理
                    ↓ /api
FastAPI：公共认证、用户、上传 / 三个独立业务 Router
                    ↓
SQLAlchemy → MySQL        图片 → backend/uploads/
```

| 层次 | 技术与职责 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite；Router 管理页面，Pinia 管理公共身份状态，Axios 统一请求 |
| 页面组件 | Naive UI 提供表单、按钮与反馈，Tailwind CSS 负责布局，公共样式统一视觉 |
| 后端 | FastAPI 提供接口，Pydantic 校验参数，SQLAlchemy 同步会话访问数据库 |
| 数据与文件 | MySQL 8、utf8mb4；图片存本地文件系统，数据库只保存图片 URL |
| 身份认证 | Argon2 保存密码哈希，JWT 校验登录身份 |

选择这一结构是为了让组员能够独立开发各自功能，同时复用账号、上传和页面基础能力；课程项目无需额外引入微服务、消息队列或容器平台。

## 3. 工程结构与分工

```text
frontend/src/
  api/                  统一请求、认证、用户、上传接口
  components/common/    通用标题、空状态、模块卡片、头像
  components/layout/    顶部导航、页面容器
  views/
    Home/ Login/ Register/ Profile/   公共页面
    Ride/ Quest/ Book/               三个模块的独立页面目录
  router/               页面路由和登录守卫
  stores/               公共认证状态
  types/                公共数据类型
  theme.ts styles.css   主题与全局样式
backend/app/
  common/               配置、数据库、密码与 Token 工具、响应与异常
  auth/ user/ files/    注册登录、用户资料、图片上传
  modules/
    ride/ quest/ book/  三个独立业务模块
  main.py               应用与 Router 注册入口
  seed.py               开发账号初始化
database/init.sql       数据库及公共用户表
docs/                   项目说明
```

| 负责范围 | 前端目录（相对 frontend/src） | 后端目录（相对 backend/app） | 接口前缀 |
| --- | --- | --- | --- |
| 公共框架负责人 | 公共页面、组件、请求、认证与主题 | common、auth、user、files | /api/auth、/api/users、/api/files |
| 拼车模块负责人 | views/Ride | modules/ride | /api/rides |
| 悬赏模块负责人 | views/Quest | modules/quest | /api/quests |
| 二手书模块负责人 | views/Book | modules/book | /api/books |

以上按职责描述分工，正式提交时由小组补充各负责人的姓名与学号。

## 4. 已提供的公共能力

### 用户与登录

注册成功后进入登录页并预填用户名；登录后可查看和修改个人资料。用户名为 3–32 位字母、数字或下划线，统一转小写且不可修改；密码为 8–128 字符；昵称为 1–32 字符，注册未填时使用用户名。

登录返回有效期 24 小时的 JWT，前端存入 localStorage，请求自动附带 `Authorization: Bearer <token>`。页面刷新时通过当前用户接口恢复身份。退出清除本地认证状态；已签发 Token 到期前仍有效，不提供刷新令牌。

公开页面包括首页、登录、注册及三个模块首页；个人中心和各模块的“我的内容”需要登录，未登录时跳转登录页，成功后返回原站内页面。未知路由显示 404。

### 公共用户表

当前只建立 `user` 表，不预先建立业务表。

| 字段 | 类型 | 用途 |
| --- | --- | --- |
| id | BIGINT，主键、自增 | 用户标识，供业务数据关联 |
| username | VARCHAR(32)，唯一 | 登录名 |
| password_hash | VARCHAR(255) | Argon2 密码哈希，不返回前端 |
| nickname | VARCHAR(32) | 显示名称 |
| avatar | VARCHAR(255)，可空 | 本服务上传图片的相对 URL |
| created_at / updated_at | DATETIME(6) | 创建和更新时间 |

建表语句在 `database/init.sql`，显式执行且不删除已有数据。应用启动不自动重建表。

### 公共接口

| 方法 | 路径 | 行为 | 登录要求 |
| --- | --- | --- | --- |
| GET | /api/health | 检查数据库连接，失败返回 503 | 无 |
| POST | /api/auth/register | username、password、可选 nickname；返回公开用户资料 | 无 |
| POST | /api/auth/login | username、password；返回 access_token、token_type、expires_in | 无 |
| GET | /api/users/me | 获取当前用户资料 | 有 |
| PUT | /api/users/me | 修改 nickname、avatar，未提交字段保持不变 | 有 |
| POST | /api/files/upload | multipart 字段 file，返回 `{url}` | 有 |

统一响应为 `{code, message, data}`，`code` 与 HTTP 状态码一致。失败时 `data` 为 null；认证失败返回 401，重名返回 409，参数校验失败返回 422，未处理的服务端错误返回 500 且不暴露内部细节。分页类型预留为 `{items, total, page, page_size}`，尚未提供业务分页接口。

上传仅接受实际内容有效的 JPEG、PNG、WebP，最大 5 MiB。文件随机命名，通过 `/uploads/` 访问；头像先上传再保存资料。头像地址只接受本服务已存在的合法上传地址，传 null 可清空。未引用文件暂不自动清理，手工删除前需确认没有用户或业务数据引用。

### 页面与样式

统一绿色主色、浅色背景、白色卡片、1200px 内容宽度和主要 12px 圆角。`AppHeader`、`AppContainer`、`PageHeader`、`EmptyState`、`ModuleCard`、`UserAvatar` 可直接复用。手机使用折叠菜单，模块页面沿用公共主题与布局。

## 5. 三个功能的接入思路

各模块当前只有公开入口 `index.vue`、受保护的 `Mine.vue` 和已挂载的空后端 Router。具体业务方案由对应负责人决定，框架提供以下共同接入方法：

1. 在自己的模块内明确页面、数据字段和接口，再开始实现；通过 `user.id` 关联用户，不另建一套注册登录。
2. 在后端模块内按需要增加 `schemas.py`、`models.py`、`service.py`，由现有 `router.py` 暴露接口。复用公共数据库基类和会话，不自行创建另一套连接。
3. 在前端模块内组织页面与接口文件，使用公共 `request` 发请求。URL 已有 `/api` 前缀，调用时不重复拼接。返回值已解包为 `data`，默认统一提示错误；页面自行提示时使用 `silent: true`。
4. 新增需要登录的页面时设置 `meta: { requiresAuth: true }`。后端使用 `CurrentUser` 校验身份，并自行校验操作对象是否属于当前用户，不能只依靠前端路由守卫。
5. 业务数据和状态保留在本模块，不塞入公共认证 Store。图片复用 `uploadImage`，页面复用公共组件和主题。

后端公共依赖的导入位置：

```python
from app.auth.dependencies import CurrentUser, DatabaseSession
from app.common.database import Base
from app.common.response import ApiResponse, PageData
```

前端模块可参照 `frontend/src/api/user.ts` 使用请求工具，例如从 `views/Ride/api.ts` 导入：

```typescript
import { request } from '../../api/request'
```

公共用户、认证、布局、请求工具和全局路由的修改需先沟通。业务建表 SQL 按模块整理，经协调后纳入统一初始化文件；已有数据库的结构变更需提供明确 SQL，不通过删库重建解决。

## 6. 交付与后续衔接

公共框架交付包括前后端源代码、环境配置示例、数据库初始化 SQL、开发账号脚本、Quick Start 和本设计说明。框架搭建时已在本机走通注册登录、三个模块入口、昵称与头像保存、刷新恢复身份、退出及登录返回原页面；前端类型检查和构建已通过。这里记录已有验证，不作为完整业务测试报告。

接棒时先按 [README](../README.md) 启动工程，检查公共流程，再在各自模块开发。每个模块完成后直接验证其主要使用流程，合并时再检查公共账号、导航、接口格式和页面样式是否一致。

结合课程考核要求，全组后续还需补齐三个业务模块的需求、数据库及程序设计说明、实际测试结果、用户使用说明和部署说明，并汇总姓名学号与工作分配。最终打包需包含前后端程序及完整初始化 SQL，按课程要求以组长学号命名；真实密钥、个人数据库凭据及本地运行数据不随包提交。
