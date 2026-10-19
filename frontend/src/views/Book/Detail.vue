<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NAlert, NButton, NCard, NImage, NModal, NSkeleton, NTag } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import UserAvatar from '../../components/common/UserAvatar.vue'
import { useAuthStore } from '../../stores/auth'
import { booksApi } from './api'
import { categoryNames, conditionNames, contactNames, formatTime, statusNames, tradeMethodNames } from './types'
import type { BookDetail, BookRelation, SellerContact } from './types'
import './book.css'
const route = useRoute(), auth = useAuthStore()
const book = ref<BookDetail>(), relation = ref<BookRelation>(), contact = ref<SellerContact>()
const loading = ref(true), busy = ref(false), error = ref(''), contactError = ref(''), notice = ref('')
const activeImage = ref(0), confirmAction = ref<'reserve' | 'unreserve' | 'sold' | 'remove' | null>(null)
const back = computed(() => { const value = String(route.query.from || ''); return /^\/book(?:\/mine)?(?:\?|$)/.test(value) ? value : '/book' })
const actionTitle = computed(() => ({ reserve: '标记已预定', unreserve: '取消预定', sold: '标记已售出', remove: '下架书籍' }[confirmAction.value || 'reserve']))
const actionText = computed(() => ({
  reserve: '标记后书摊会提示“已预定”，你仍可在交易变化时取消预定。',
  unreserve: '取消预定后书籍重新显示为在售状态，其他同学可以继续联系你。',
  sold: '标记已售出后，书籍将从书摊下架，且不能恢复为在售。',
  remove: '下架后书籍从书摊移除，且不能恢复为在售；历史记录仍保留在“我的书籍”中。',
}[confirmAction.value || 'reserve']))
let revision = 0
async function load() {
  const version = ++revision
  book.value = undefined; relation.value = undefined; contact.value = undefined; contactError.value = ''; loading.value = true; error.value = ''
  try {
    const data = await booksApi.detail(Number(route.params.id)); if (version !== revision) return
    book.value = data; activeImage.value = 0
    if (auth.isAuthenticated) { const rel = await booksApi.relation(data.id); if (version === revision) relation.value = rel }
  } catch (e) { if (version === revision) error.value = e instanceof Error ? e.message : '书籍加载失败' } finally { if (version === revision) loading.value = false }
}
async function loadContact() {
  const version = revision; contactError.value = ''
  try { const data = await booksApi.contact(Number(route.params.id)); if (version === revision) contact.value = data }
  catch (e) { if (version === revision) contactError.value = e instanceof Error ? e.message : '无法获取联系方式' }
}
async function toggleFavorite() {
  if (!book.value || !relation.value || busy.value) return
  busy.value = true
  try { const result = await booksApi.favorite(book.value.id, !relation.value.is_favorited); book.value.favorite_count = result.favorite_count; relation.value.is_favorited = result.is_favorited }
  catch (e) { error.value = e instanceof Error ? e.message : '操作失败' } finally { busy.value = false }
}
async function act() {
  if (!confirmAction.value || !book.value || busy.value) return
  busy.value = true
  try { await booksApi.act(book.value.id, confirmAction.value); notice.value = '操作已保存'; confirmAction.value = null; await load() }
  catch (e) { confirmAction.value = null; error.value = e instanceof Error ? e.message : '操作失败' } finally { busy.value = false }
}
watch(() => [route.params.id, auth.token], () => { confirmAction.value = null; contact.value = undefined; relation.value = undefined; notice.value = route.query.saved ? '书籍已保存' : ''; void load() }, { immediate: true })
</script>
<template>
 <AppContainer><main class="book-page">
  <PageHeader title="书籍详情" description="看看这本书，是否正是你要找的。"><template #actions><RouterLink :to="back"><NButton quaternary>返回书籍列表</NButton></RouterLink></template></PageHeader>
  <NAlert v-if="notice" type="success" class="book-error" closable @close="notice = ''">{{ notice }}</NAlert>
  <NAlert v-if="error" type="error" class="book-error">{{ error }} <NButton text @click="load">重新加载</NButton></NAlert>
  <NSkeleton v-if="loading" text :repeat="8" />
  <div v-else-if="book" class="book-detail-grid">
   <div>
    <NCard class="book-section">
     <div class="book-gallery-main"><NImage :src="book.cover_images[activeImage]" :alt="book.title" object-fit="cover" style="width:100%;height:100%" /></div>
     <div v-if="book.cover_images.length > 1" class="book-gallery-thumbs">
      <button v-for="(url, index) in book.cover_images" :key="url" type="button" class="book-gallery-thumb" :class="{ active: index === activeImage }" @click="activeImage = index"><img :src="url" :alt="`缩略图 ${index + 1}`" /></button>
     </div>
     <div class="book-detail-meta" style="margin-top:22px">
      <NTag :bordered="false" type="info">{{ categoryNames[book.category] }}</NTag>
      <NTag :bordered="false">{{ conditionNames[book.condition_grade] }}</NTag>
      <NTag v-if="book.status !== 'listed'" :bordered="false" :type="book.status === 'reserved' ? 'warning' : 'default'">{{ statusNames[book.status] }}</NTag>
     </div>
     <h2 class="book-detail-title">{{ book.title }}</h2>
     <p class="book-detail-author">{{ book.author }}<span v-if="book.isbn"> · ISBN {{ book.isbn }}</span></p>
     <div class="book-price-block"><span class="book-price-now">¥{{ book.price }}</span><span v-if="book.original_price" class="book-price-original">¥{{ book.original_price }}</span><NTag v-if="book.is_negotiable" :bordered="false" type="warning">可议价</NTag></div>
     <dl class="book-detail-list">
      <div><dt>书籍描述</dt><dd class="book-note">{{ book.description }}</dd></div>
      <div><dt>交易方式</dt><dd>{{ tradeMethodNames[book.trade_method] }}</dd></div>
      <div><dt>交易地点</dt><dd>{{ book.trade_location }}</dd></div>
     </dl>
     <p class="book-muted">发布于 {{ formatTime(book.created_at) }} · {{ book.view_count }} 次浏览 · {{ book.favorite_count }} 人收藏</p>
    </NCard>
   </div>
   <div>
    <NCard class="book-section">
     <div class="book-people"><UserAvatar :user="book.seller" :size="44" /><div><strong>{{ book.seller.nickname }}</strong><div class="book-muted">书籍发布者</div></div></div>
     <template v-if="!auth.isAuthenticated"><RouterLink :to="{ path: '/login', query: { redirect: route.fullPath } }"><NButton type="primary" block style="margin-top:18px">登录后联系卖家</NButton></RouterLink></template>
     <template v-else-if="relation">
      <NTag v-if="relation.is_owner" :bordered="false" style="margin-top:18px">你发布的书籍</NTag>
      <div class="book-actions" style="margin-top:18px">
       <NButton v-if="!relation.is_owner" :disabled="busy" @click="toggleFavorite">{{ relation.is_favorited ? '✓ 已收藏' : '♡ 收藏' }}</NButton>
       <RouterLink v-if="relation.can_edit" :to="`/book/${book.id}/edit`"><NButton :disabled="busy">编辑信息</NButton></RouterLink>
       <NButton v-if="relation.can_reserve" :disabled="busy" @click="confirmAction = 'reserve'">标记已预定</NButton>
       <NButton v-if="relation.can_unreserve" :disabled="busy" @click="confirmAction = 'unreserve'">取消预定</NButton>
       <NButton v-if="relation.can_mark_sold" type="primary" :disabled="busy" @click="confirmAction = 'sold'">标记已售出</NButton>
       <NButton v-if="relation.can_remove" :disabled="busy" @click="confirmAction = 'remove'">下架书籍</NButton>
      </div>
      <p v-if="!relation.can_contact && !relation.is_owner" class="book-muted" style="margin-top:14px">{{ statusNames[book.status] }}，暂时无法联系卖家。</p>
     </template>
    </NCard>
    <NCard v-if="relation?.can_contact" title="联系卖家" style="margin-top:20px">
     <NAlert v-if="contactError" type="warning">{{ contactError }}</NAlert>
     <NButton v-if="!contact" @click="loadContact">查看联系方式</NButton>
     <div v-else class="book-people"><UserAvatar :user="contact" :size="32" /><div><strong>{{ contact.nickname }}</strong><div>{{ contactNames[contact.contact_type] }}：{{ contact.contact_value }}</div></div></div>
     <p class="book-muted" style="margin-top:12px">线下交易时请核对书籍成色，注意自身财物与人身安全。</p>
    </NCard>
   </div>
  </div>
  <NModal :show="Boolean(confirmAction)" preset="dialog" :title="actionTitle" :positive-text="actionTitle" negative-text="暂不操作" :loading="busy" :mask-closable="!busy" :closable="!busy" @positive-click="act" @negative-click="confirmAction = null" @close="confirmAction = null"><p>{{ actionText }}</p></NModal>
 </main></AppContainer>
</template>
