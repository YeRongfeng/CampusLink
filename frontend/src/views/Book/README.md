# Book 开发空间

校园二手书模块：书摊 /book、发布 /book/new、详情 /book/:id、编辑 /book/:id/edit、我的书籍 /book/mine（我发布的、我收藏的）。
`components/BookList.vue` 承载书摊与我的书籍共用的筛选、分页和卡片展示；`components/ImagePicker.vue` 提供多图上传、选封面和删除。
接口前缀 /api/books，统一使用 src/api/request.ts，不直接使用 Axios。
