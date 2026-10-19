<script setup lang="ts">
import { NTag } from 'naive-ui'
import { categoryNames, conditionNames, statusNames } from '../types'
import type { Book } from '../types'
defineProps<{ book: Book; returnTo: string }>()
</script>
<template>
  <RouterLink class="book-card" :to="{ path: `/book/${book.id}`, query: { from: returnTo } }">
    <div class="book-card-cover">
      <img :src="book.cover_image" :alt="book.title" loading="lazy" />
      <NTag v-if="book.status !== 'listed'" class="book-card-status" round :bordered="false" :type="book.status === 'reserved' ? 'warning' : 'default'">{{ statusNames[book.status] }}</NTag>
      <NTag v-if="book.discount_percent" class="book-card-discount" round :bordered="false" type="error">{{ book.discount_percent }}% OFF</NTag>
    </div>
    <div class="book-card-body">
      <div class="book-card-top"><span>{{ categoryNames[book.category] }}</span><span>{{ conditionNames[book.condition_grade] }}</span></div>
      <h3>{{ book.title }}</h3>
      <p class="book-card-author">{{ book.author }}</p>
      <div class="book-card-price"><strong>¥{{ book.price }}</strong><span v-if="book.original_price" class="book-card-original">¥{{ book.original_price }}</span><span v-if="book.is_negotiable" class="book-card-negotiable">可议价</span></div>
      <div class="book-card-footer"><span>♡ {{ book.favorite_count }}</span><span>{{ book.view_count }} 次浏览</span></div>
    </div>
  </RouterLink>
</template>
<style scoped>
.book-card{display:flex;flex-direction:column;border:1px solid var(--border);background:white;border-radius:12px;color:var(--text-primary);text-decoration:none;transition:box-shadow .2s,border-color .2s;overflow:hidden;min-width:0}
.book-card:hover{border-color:#a4cbb0;box-shadow:0 8px 26px #2847320b}
.book-card-cover{position:relative;aspect-ratio:4/3;background:#edf3ed}
.book-card-cover img{width:100%;height:100%;object-fit:cover;display:block}
.book-card-status{position:absolute;top:10px;left:10px}
.book-card-discount{position:absolute;top:10px;right:10px}
.book-card-body{padding:16px 18px 18px;display:flex;flex-direction:column;flex:1}
.book-card-top{display:flex;justify-content:space-between;gap:8px;font-size:11px;letter-spacing:1px;color:#819187;margin-bottom:10px}
.book-card h3{font-size:16px;line-height:1.5;margin:0 0 4px;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.book-card-author{font-size:12px;color:var(--text-secondary);margin:0 0 14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.book-card-price{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.book-card-price strong{font-size:20px;color:var(--primary)}
.book-card-original{font-size:12px;color:#a0ada4;text-decoration:line-through}
.book-card-negotiable{font-size:11px;color:#f0a020;border:1px solid #f0a020;border-radius:6px;padding:1px 6px}
.book-card-footer{display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--border);padding-top:12px;margin-top:auto;font-size:12px;color:var(--text-secondary)}
</style>
