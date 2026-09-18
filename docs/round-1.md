# 第一轮验收记录

日期：2026-09-17。范围：工程初始化、前后端连通、本机 MySQL。

| 检查 | 结果 |
| --- | --- |
| 前端依赖安装 | 通过，精确版本和锁文件已生成 |
| 后端依赖安装及 pip check | 通过，requirements.txt 固定版本，无依赖冲突 |
| npm run build | 通过，含 TypeScript 检查 |
| 后端健康与配置测试 | 3 项通过，不操作真实数据库 |
| uvicorn --reload / npm run dev | 均正常启动 |
| 浏览器 → 开发代理 → FastAPI → MySQL | 页面显示连接正常，HTTP 200 |
| 真实停止 MySQL 后请求 | HTTP 503，data 为 null，页面正确提示 |
| MySQL 重启后的恢复 | 无需重启后端，代理恢复 HTTP 200，浏览器重新显示连接正常 |
| FastAPI /docs | HTTP 200 |

后端测试有两条上游弃用提示：Starlette 的 httpx 支持、AnyIO 的 BlockingPortal 别名。当前测试通过，未屏蔽提示，后续统一升级依赖时处理。

本机 MySQL 8.4.11 位于被忽略的 .local 目录，仅监听 127.0.0.1:3306，不注册系统服务。管理员凭据保存在 .local/mysql-admin.cnf，应用凭据保存在 backend/.env，不提交 Git。

Windows 中文路径已通过系统编码配置和相对命令参数适配。已有 MySQL 的开发者也可以手动执行 init.sql 并配置 .env。

**轮次边界：**等待用户检查第一轮后进入第二轮；尚未实现用户表、注册登录、个人中心、业务模块占位页及上传。
