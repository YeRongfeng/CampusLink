# 业务模块开发空间

ride、quest、book 分别使用 /api/rides、/api/quests、/api/books 前缀。
当前 Router 已挂载但为空，无业务接口或数据表。

开发时使用 app.auth.dependencies.CurrentUser 获取已认证用户，使用 DatabaseSession 获取请求会话，使用 ApiResponse 返回统一响应。
直接在各自 Router 中添加接口；不要自行修改 User、认证或公共响应约定。
