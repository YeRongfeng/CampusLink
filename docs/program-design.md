# 程序设计说明书

## 结构与职责

系统采用前后端分离的单体分模块结构，详细目录见 [框架设计](framework.md)。

- 前端：页面负责交互；公共组件负责布局；`api/request.ts` 负责请求、Token、超时及错误提示；Pinia 管理 `token`、`currentUser`，派生 `isAuthenticated`。
- 后端：Router 定义路径，Schema 校验和描述数据，Service 处理用户业务，Model 映射数据库。`common` 提供配置、数据库、密码与 JWT、响应和异常处理。
- 每个请求通过依赖获取同步 SQLAlchemy Session，请求结束关闭；写入由服务层显式提交。

## 接口契约

前缀统一为 `/api`。除上传使用 multipart 外，请求体为 JSON；需登录接口使用 `Authorization: Bearer <access_token>`。正常结果均为 HTTP 200：

```json
{"code":200,"message":"success","data":{}}
```

失败示例：

```json
{"code":401,"message":"请先登录或重新登录","data":null}
```

客户端按状态码处理错误，不依赖错误文案逐字匹配。常用状态：401 身份无效、409 用户名重复、413 文件超限、415 图片不合法、422 参数错误、500 服务端异常、503 健康检查数据库不可用。

| 方法与路径 | 请求 | data 内容 |
| --- | --- | --- |
| GET /api/health | 无 | `{status: "ok"}` |
| POST /api/auth/register | username、password、可选 nickname | 公开用户对象 |
| POST /api/auth/login | username、password | access_token、token_type（bearer）、expires_in（86400 秒） |
| GET /api/users/me | 无，需登录 | 公开用户对象 |
| PUT /api/users/me | 可选 nickname、avatar，需登录 | 更新后的公开用户对象 |
| POST /api/files/upload | multipart 的 file 字段，需登录 | `{url: "/uploads/文件名"}` |

公开用户对象包含 `id、username、nickname、avatar、created_at、updated_at`。注册可省略或传 null 的昵称采用用户名；资料更新省略的字段保持原值，nickname 不接受 null 或空白，avatar 传 null 清空，空对象不改变资料。用户名及未知字段不能通过资料更新修改。

例如仅修改昵称：

```http
PUT /api/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{"nickname":"校园同学"}
```

上传限制为 5 MiB 的 JPEG、PNG、WebP；实际图片验证通过后随机命名存储。上传仅返回 URL，不自动绑定到用户；前端再发送 `{"avatar":"/uploads/返回的文件名"}` 更新资料。

详细字段与可执行请求参见运行后的 `/docs`。分页公共类型为 `{items,total,page,page_size}`，目前没有业务分页接口。

## 关键流程

1. 注册：校验并规范用户名 → 检查重复 → Argon2 哈希 → 写入用户 → 返回公开资料 → 前端进入登录页。
2. 登录：校验用户名与密码 → 签发 24 小时 JWT → 前端存储 Token 并获取当前用户。刷新时调用 `/users/me` 验证身份。
3. 访问受保护资源：前端守卫引导登录；后端独立解析 Token 并查询用户。Token 过期或无效返回 401，前端清除相应认证状态。
4. 修改头像：校验本地文件 → 上传 → 更新用户头像 URL → 显示新头像。任一步失败时提示重试，原头像不被替换。
5. 退出：仅清除本地登录状态，不设置服务端黑名单，已签发 Token 到期前仍可使用。

## 模块扩展约定

前端公开入口为 `/ride、/quest、/book`，个人入口追加 `/mine`。后端空 Router 已分别挂载到 `/api/rides、/api/quests、/api/books`，尚无业务操作接口。

模块使用公共 `CurrentUser、DatabaseSession、ApiResponse`，前端使用 `request`（路径不重复写 `/api`，结果已经解包）。业务权限需由模块验证记录归属，不能仅相信前端传来的用户 ID。新增路由和公共层修改先协调，保持接口简单、一种操作一种明确含义，不引入无需求的通用接口。
