# Ride 开发空间

校园拼车模块：大厅 /ride、我的行程 /ride/mine、发布 /ride/new、详情 /ride/:id、编辑 /ride/:id/edit。共享 LocationPicker 为三个地点提供搜索、地图选点和主动定位，未配置地图时可手动输入。
接口前缀 /api/rides，统一使用 src/api/request.ts，不直接使用 Axios。
