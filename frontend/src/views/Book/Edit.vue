<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NCheckbox, NInput, NInputNumber, NSelect, NSkeleton } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import ImagePicker from './components/ImagePicker.vue'
import { booksApi } from './api'
import { categoryOptions, conditionOptions, contactOptions, tradeMethodOptions } from './types'
import type { BookWrite } from './types'
import './book.css'
const route = useRoute(), router = useRouter(), id = route.params.id ? Number(route.params.id) : undefined
const busy = ref(false), loading = ref(Boolean(id)), error = ref(''), loadFailed = ref(false), saved = ref(false)
const model = reactive<Omit<BookWrite, 'price' | 'original_price'>>({ title: '', author: '', isbn: null, category: 'textbook', condition_grade: 'good', description: '', cover_images: [], is_negotiable: false, trade_method: 'meetup', trade_location: '', contact_type: 'wechat', contact_value: '' })
const price = ref<number | null>(null), originalPrice = ref<number | null>(null), baseline = ref('')
const snapshot = () => JSON.stringify([model, price.value, originalPrice.value])
const dirty = computed(() => Boolean(baseline.value) && snapshot() !== baseline.value && !saved.value)
async function load() {
  loading.value = Boolean(id); error.value = ''; loadFailed.value = false
  if (id) try {
    const [book, relation] = await Promise.all([booksApi.detail(id), booksApi.relation(id)])
    if (!relation.can_edit) throw new Error('仅本人发布、尚在售的书籍可以编辑')
    const contact = await booksApi.contact(id).catch(() => null)
    Object.assign(model, { title: book.title, author: book.author, isbn: book.isbn, category: book.category, condition_grade: book.condition_grade, description: book.description, cover_images: [...book.cover_images], is_negotiable: book.is_negotiable, trade_method: book.trade_method, trade_location: book.trade_location })
    price.value = Number(book.price); originalPrice.value = book.original_price === null ? null : Number(book.original_price)
    if (contact) { model.contact_type = contact.contact_type; model.contact_value = contact.contact_value }
  } catch (e) { error.value = e instanceof Error ? e.message : '无法加载书籍信息'; loadFailed.value = true }
  loading.value = false; baseline.value = snapshot()
}
async function submit() {
  if (busy.value) return
  error.value = ''
  if (model.title.trim().length < 1) { error.value = '请填写书名'; return }
  if (model.author.trim().length < 1) { error.value = '请填写作者'; return }
  if (model.description.trim().length < 5) { error.value = '请填写至少 5 个字符的书籍描述'; return }
  if (!model.cover_images.length) { error.value = '请至少上传 1 张书籍图片'; return }
  if (price.value === null || price.value < 0) { error.value = '请填写合理的价格'; return }
  if (originalPrice.value !== null && originalPrice.value < price.value) { error.value = '原价不能低于现价'; return }
  if (model.trade_location.trim().length < 2) { error.value = '请填写至少 2 个字符的交易地点'; return }
  if (model.contact_value.trim().length < 3) { error.value = '请填写有效的联系方式，至少 3 个字符'; return }
  busy.value = true
  try {
    const result = await booksApi.save({ ...model, price: price.value.toFixed(2), original_price: originalPrice.value === null ? null : originalPrice.value.toFixed(2) }, id)
    saved.value = true; await router.push({ path: `/book/${result.id}`, query: { saved: '1', from: '/book/mine' } })
  } catch (e) { error.value = (e instanceof Error ? e.message : '保存失败') + '。若网络中断，请先在“我的书籍”确认是否已保存。' } finally { busy.value = false }
}
function leaving(event: BeforeUnloadEvent) { if (dirty.value) { event.preventDefault(); event.returnValue = '' } }
onMounted(() => { void load(); window.addEventListener('beforeunload', leaving) })
onBeforeUnmount(() => window.removeEventListener('beforeunload', leaving))
onBeforeRouteLeave(() => !dirty.value || window.confirm('尚有未保存的内容，确定离开吗？'))
</script>
<template>
 <AppContainer><main class="book-page book-form">
  <PageHeader :title="id ? '编辑书籍' : '发布书籍'" description="把闲置的书，交给需要它的同学。"><template #actions><RouterLink to="/book"><NButton quaternary>返回书摊</NButton></RouterLink></template></PageHeader>
  <NAlert v-if="error" type="error" class="book-error" aria-live="polite">{{ error }} <NButton v-if="loadFailed" text @click="load">重新加载</NButton></NAlert>
  <NSkeleton v-if="loading" text :repeat="8" />
  <form v-else-if="!loadFailed" @submit.prevent="submit">
   <NCard class="book-section"><h2>书籍信息</h2><div class="book-form-grid">
    <div class="book-field"><label for="book-title">书名 *</label><NInput id="book-title" v-model:value="model.title" :maxlength="120" :disabled="busy" placeholder="例如：高等数学（上册）第七版" /></div>
    <div class="book-field"><label for="book-author">作者 *</label><NInput id="book-author" v-model:value="model.author" :maxlength="80" :disabled="busy" placeholder="例如：同济大学数学系" /></div>
    <div class="book-field"><label for="book-isbn">ISBN（选填）</label><NInput id="book-isbn" v-model:value="model.isbn" :maxlength="20" :disabled="busy" placeholder="例如：978-7-04-039660-6" /></div>
    <div class="book-field"><label>分类 *</label><NSelect v-model:value="model.category" :options="categoryOptions" :disabled="busy" /></div>
    <div class="book-field"><label>成色 *</label><NSelect v-model:value="model.condition_grade" :options="conditionOptions" :disabled="busy" /></div>
    <div class="book-field full"><label for="book-description">书籍描述 *</label><NInput id="book-description" v-model:value="model.description" type="textarea" :maxlength="1000" show-count :disabled="busy" :autosize="{ minRows: 3, maxRows: 6 }" placeholder="成色细节、笔记划线情况、版次等，越详细越容易成交" /></div>
    <div class="book-field full"><label>书籍图片 *</label><ImagePicker v-model="model.cover_images" /></div>
   </div></NCard>
   <NCard class="book-section"><h2>价格</h2><div class="book-form-grid">
    <div class="book-field"><label for="book-price">现价（元）*</label><NInputNumber id="book-price" v-model:value="price" :disabled="busy" :min="0" :max="9999.99" :precision="2" placeholder="转手价格" /></div>
    <div class="book-field"><label for="book-original-price">原价（元，选填）</label><NInputNumber id="book-original-price" v-model:value="originalPrice" :disabled="busy" :min="0" :max="9999.99" :precision="2" placeholder="留空则不显示折扣" /></div>
    <div class="book-field full"><NCheckbox v-model:checked="model.is_negotiable" :disabled="busy">价格可议</NCheckbox></div>
   </div></NCard>
   <NCard class="book-section"><h2>交易方式与联系方式</h2><div class="book-form-grid">
    <div class="book-field"><label>交易方式 *</label><NSelect v-model:value="model.trade_method" :options="tradeMethodOptions" :disabled="busy" /></div>
    <div class="book-field"><label for="book-location">交易地点 *</label><NInput id="book-location" v-model:value="model.trade_location" :maxlength="160" :disabled="busy" placeholder="例如：图书馆东门、宿舍楼下" /></div>
    <div class="book-field"><label>联系类型 *</label><NSelect v-model:value="model.contact_type" :options="contactOptions" :disabled="busy" aria-label="联系类型" /></div>
    <div class="book-field"><label for="book-contact">联系方式 *</label><NInput id="book-contact" v-model:value="model.contact_value" :maxlength="64" :disabled="busy" placeholder="填写方便联系你的账号或号码" /></div>
   </div><p class="book-muted">联系方式仅对有意向的同学开放。发布后，书籍信息、价格和交易地点将公开展示。</p></NCard>
   <div class="book-actions" style="justify-content:flex-end"><RouterLink to="/book/mine"><NButton :disabled="busy">我的书籍</NButton></RouterLink><NButton attr-type="submit" type="primary" size="large" :loading="busy">{{ id ? '保存修改' : '发布书籍' }}</NButton></div>
  </form>
 </main></AppContainer>
</template>
