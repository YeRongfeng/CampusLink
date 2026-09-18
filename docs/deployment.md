# 系统部署维护说明

## 适用范围

本说明用于整组应用的部署与维护。当前已填写公共框架在 Windows 本机课程开发环境中的运行方式；三个模块新增配置及最终交付环境预留在后文，尚未完成生产部署方案。环境为 Node.js 22.12+、Python 3.12、MySQL 8；安装和启动命令见 [Quick Start](../README.md)。默认服务仅监听本机，前端 5173、后端 8000、MySQL 3306。

## 已有公共配置与本地启动

后端使用 `backend/.env`，由 `.env.example` 复制后填写：

| 变量 | 含义 |
| --- | --- |
| DATABASE_HOST / DATABASE_PORT | MySQL 地址与端口 |
| DATABASE_NAME | 默认 campuslink |
| DATABASE_USER / DATABASE_PASSWORD | 对项目库有读写权限的数据库账号 |
| JWT_SECRET | 随机生成且至少 32 字符，拒绝示例占位值 |

不要覆盖同学已有 `.env`；真实密码、密钥不得提交仓库。前端默认无需配置，若修改后端端口，参照 `frontend/.env.example` 设置 `BACKEND_PROXY_TARGET` 并重启前端；VITE_ 变量会暴露给浏览器，不存凭据。

启动顺序：MySQL → 执行 `database/init.sql`（首次或需要补建表时）→ FastAPI → Vite。健康检查 `/api/health` 返回 200 表示数据库可连，API 文档位于 `/docs`。终端中按 Ctrl+C 停止前后端。

使用项目本地 MySQL 脚本的电脑可在根目录执行 `backend/.venv/Scripts/python.exe database/local_mysql.py start` 或 `stop`。脚本依赖 `.local/mysql-8.4.11-winx64/`，不会随 Git 克隆；普通 MySQL 安装不需要此脚本。不要对已有环境重复执行 setup。

## 数据维护与恢复

`backend/uploads/` 自动创建，保存头像等图片。未引用文件不自动清理，删除前先查询所有引用它的用户和业务数据。

备份前暂停应用写入，使用 MySQL 工具备份数据库，同时复制 `backend/uploads/`；将 `.env` 单独保管在受限位置。备份文件含用户数据，不放入仓库。已安装 MySQL 客户端时，可执行以下示例，按实际账号和库名替换，文件保存至项目外的备份目录：

```powershell
mysqldump -u <数据库账号> -p --single-transaction --no-tablespaces --set-gtid-purged=OFF --result-file=<备份文件绝对路径> campuslink
```

恢复时停止应用，先备份现有状态，在确认目标库后通过 MySQL 客户端导入 SQL，再恢复对应 uploads 目录并启动应用检查资料与头像。恢复会改变目标库数据，不可直接对唯一开发库试验。备份恢复流程尚未做实际演练。

结构更新通过明确 SQL 执行，`CREATE TABLE IF NOT EXISTS` 不会修改已有表。更换 JWT_SECRET 会使旧 Token 失效，用户需重新登录。

## 排障与交付

| 现象 | 检查方式 |
| --- | --- |
| 后端无法启动 | 检查虚拟环境依赖、.env、JWT_SECRET 是否为真实随机值 |
| 健康检查 503 | 检查 MySQL 是否启动、账号权限、数据库名和端口 |
| 前端请求失败 | 检查 8000 端口及代理配置，修改配置后重启 |
| 头像不显示 | 检查 uploads 文件是否存在、后端静态服务及开发代理 |
| 端口被占用 | 停止对应旧服务，或协调修改端口与代理 |

前端在 `frontend` 目录执行 `npm run build`，产物为 `dist/`。`npm run preview` 不提供当前开发代理，不能当作完整前后端部署。最终部署目标确定后，需补充静态文件托管、API 与 uploads 转发方案。

交付包应包含源代码、锁文件、配置示例、完整数据库 SQL 和文档；不附带真实凭据、node_modules、虚拟环境或 MySQL 数据目录。全组业务完成后按课程要求以组长学号命名归档文件。

## 模块部署补充（各模块负责人填写）

| 模块 | 新增依赖与环境变量 | 初始化 SQL / 数据 | 文件目录及维护事项 |
| --- | --- | --- | --- |
| 校园拼车 | 待确认；无新增则写“无” | 待补充 | 待补充 |
| 校园悬赏 | 待确认；无新增则写“无” | 待补充 | 待补充 |
| 二手书 | 待确认；无新增则写“无” | 待补充 | 待补充 |

## 全系统交付部署（集成负责人补充）

待确定最终运行环境、实际端口与访问地址、完整初始化顺序、前端静态资源及接口转发、启动停止方法、日志位置，以及更新和回退步骤。按实际部署环境填写，不默认必须上云。

业务完成后汇总全部数据库表与文件目录的备份恢复方法，在目标环境实际验证后记录日期和结果；当前本地启动说明不能替代最终部署验收。
