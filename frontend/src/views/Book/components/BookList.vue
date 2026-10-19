<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NCheckbox, NInput, NInputNumber, NPagination, NSelect, NSkeleton, NTabs, NTab } from 'naive-ui'
import AppContainer from '../../../components/layout/AppContainer.vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import BookCard from './BookCard.vue'
import { booksApi } from '../api'
import { categoryOptions, conditionOptions, tradeMethodOptions } from '../types'
import type { Book, Page } from '../types'
import '../book.css'
const props = defineProps<{ mine?: boolean }>()
const route = useRoute(), router = useRouter()
const filters = reactive({ keyword: '', category: null as string | null, condition_grade: null as string | null, trade_method: null as string | null, price_min: null as number | null, price_max: null as number | null, negotiable: false, available: false })
const sort = ref<'latest' | 'price_asc' | 'price_desc'>('latest')
const sortOptions = [{ value: 'latest', label: '最新发布' }, { value: 'price_asc', label: '价格从低到高' }, { value: 'price_desc', label: '价格从高到低' }]
const scope = ref('selling'), page = ref(1), busy = ref(false), error = ref('')
const result = ref<Page<Book>>({ items: [], total: 0, page: 1, page_size: 12 })
let revision = 0
async function load() {
  const version = ++revision
  filters.keyword = String(route.query.keyword || '').slice(0, 120)
  filters.category = typeof route.query.category === 'string' ? route.query.category : null
  filters.condition_grade = typeof route.query.condition_grade === 'string' ? route.query.condition_grade : null
  filters.trade_method = typeof route.query.trade_method === 'string' ? route.query.trade_method : null
  filters.price_min = route.query.price_min ? Number(route.query.price_min) : null
  filters.price_max = route.query.price_max ? Number(route.query.price_max) : null
  filters.negotiable = route.query.negotiable === '1'
  filters.available = route.query.available === '1'
  sort.value = (['latest', 'price_asc', 'price_desc'].includes(String(route.query.sort)) ? route.query.sort : 'latest') as typeof sort.value
  scope.value = route.query.scope === 'favorites' ? 'favorites' : 'selling'
  page.value = Math.min(100000, Math.max(1, Math.floor(Number(route.query.page) || 1)))
  busy.value = true; error.value = ''
  try {
    const data = await booksApi.list(props.mine ? { scope: scope.value, page: page.value } : {
      keyword: filters.keyword || undefined, category: filters.category || undefined,
      condition_grade: filters.condition_grade || undefined, trade_method: filters.trade_method || undefined,
      price_min: filters.price_min ?? undefined, price_max: filters.price_max ?? undefined,
      negotiable_only: filters.negotiable, available_only: filters.available, sort: sort.value, page: page.value,
    }, props.mine)
    if (version === revision) result.value = data
  } catch (e) { if (version === revision) error.value = e instanceof Error ? e.message : '加载失败' }
  finally { if (version === revision) busy.value = false }
}
function search(p = 1) {
  const query = props.mine ? { scope: scope.value, page: String(p) } : {
    keyword: filters.keyword || undefined, category: filters.category || undefined,
    condition_grade: filters.condition_grade || undefined, trade_method: filters.trade_method || undefined,
    price_min: filters.price_min != null ? String(filters.price_min) : undefined,
    price_max: filters.price_max != null ? String(filters.price_max) : undefined,
    negotiable: filters.negotiable ? '1' : undefined, available: filters.available ? '1' : undefined,
    sort: sort.value === 'latest' ? undefined : sort.value, page: String(p),
  }
  const target = router.resolve({ path: route.path, query }).fullPath
  if (target === route.fullPath) void load(); else void router.push({ query })
}
function reset() { Object.assign(filters, { keyword: '', category: null, condition_grade: null, trade_method: null, price_min: null, price_max: null, negotiable: false, available: false }); sort.value = 'latest'; search() }
watch(() => route.fullPath, load, { immediate: true })
</script>
<template>
 <AppContainer><main class="book-page">
  <p class="eyebrow">CAMPUS BOOK · 好书不落灰</p>
  <PageHeader :title="mine ? '我的书籍' : '校园二手书'" :description="mine ? '发布的书籍和收藏的好书都在这里。' : '把读过的书，交给下一位需要的同学。'">
   <template #actions><div class="book-actions"><RouterLink :to="mine ? '/book' : '/book/mine'"><NButton>{{ mine ? '逛逛书摊' : '我的书籍' }}</NButton></RouterLink><RouterLink to="/book/new"><NButton type="primary">发布书籍</NButton></RouterLink></div></template>
  </PageHeader>
  <div v-if="!mine" class="book-intro">教材、教辅、考试资料或闲置读物，标好成色和价格，就能遇到下一位主人。</div>
  <NTabs v-if="mine" v-model:value="scope" type="line" style="margin-bottom:24px" @update:value="search(1)"><NTab name="selling">我发布的</NTab><NTab name="favorites">我收藏的</NTab></NTabs>
  <NCard v-else><form @submit.prevent="search(1)">
    <div class="book-filters">
      <div class="book-field"><label for="book-keyword">书名或作者</label><NInput id="book-keyword" v-model:value="filters.keyword" :maxlength="120" placeholder="搜索想找的书" /></div>
      <div class="book-field"><label>分类</label><NSelect v-model:value="filters.category" :options="categoryOptions" clearable placeholder="全部分类" /></div>
      <div class="book-field"><label>成色</label><NSelect v-model:value="filters.condition_grade" :options="conditionOptions" clearable placeholder="全部成色" /></div>
      <div class="book-field"><label>交易方式</label><NSelect v-model:value="filters.trade_method" :options="tradeMethodOptions" clearable placeholder="不限方式" /></div>
    </div>
    <div class="book-filters-row2">
      <div class="book-field"><label for="book-price-min">最低价</label><NInputNumber id="book-price-min" v-model:value="filters.price_min" :min="0" :max="9999.99" :precision="2" placeholder="不限" style="width:100%" /></div>
      <div class="book-field"><label for="book-price-max">最高价</label><NInputNumber id="book-price-max" v-model:value="filters.price_max" :min="0" :max="9999.99" :precision="2" placeholder="不限" style="width:100%" /></div>
      <div class="book-field"><label>排序方式</label><NSelect v-model:value="sort" :options="sortOptions" /></div>
      <div class="book-filter-toggles"><NCheckbox v-model:checked="filters.negotiable">可议价</NCheckbox><NCheckbox v-model:checked="filters.available">仅看在售</NCheckbox></div>
    </div>
    <div class="book-filter-actions"><NButton attr-type="submit" type="primary">查找书籍</NButton><NButton quaternary @click="reset">重置</NButton></div>
  </form></NCard>
  <div class="book-filter-bottom"><span class="book-muted">{{ busy ? '正在查找书籍…' : `共 ${result.total} 本书` }}</span></div>
  <NAlert v-if="error" type="error" class="book-error">{{ error }} <NButton text @click="load">重新加载</NButton></NAlert>
  <div v-if="busy" class="book-grid"><NCard v-for="n in 3" :key="n"><NSkeleton text :repeat="5" /></NCard></div>
  <div v-else-if="!error && result.items.length" class="book-grid"><BookCard v-for="book in result.items" :key="book.id" :book="book" :return-to="route.fullPath" /></div>
  <NCard v-else-if="!error"><div class="book-empty"><h2>{{ mine ? '还没有相关书籍' : '暂时没有符合条件的书' }}</h2><p>{{ mine ? '去书摊看看，或发布一本闲置书。' : '换个关键词或分类试试，也可以先发布一本。' }}</p><RouterLink to="/book/new"><NButton type="primary">发布书籍</NButton></RouterLink></div></NCard>
  <div v-if="!error && result.total > 12" class="book-pagination"><NPagination :page="page" :item-count="result.total" :page-size="12" :page-slot="5" @update:page="search" /></div>
 </main></AppContainer>
</template>
