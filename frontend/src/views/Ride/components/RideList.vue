<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NCheckbox, NInput, NPagination, NSelect, NSkeleton, NTabs, NTab } from 'naive-ui'
import AppContainer from '../../../components/layout/AppContainer.vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import RideCard from './RideCard.vue'
import LocationPicker from './LocationPicker.vue'
import { ridesApi } from '../api'
import type { Location, Page, Ride } from '../types'
import '../ride.css'
const props = defineProps<{ mine?: boolean }>()
const route = useRoute(), router = useRouter()
const filters = reactive({ origin: '', destination: '', date: '', available: false })
type Endpoint = 'origin' | 'destination'
const endpoints: { key: Endpoint; label: string; placeholder: string }[] = [
  { key: 'origin', label: '出发地', placeholder: '学校、校门或车站' },
  { key: 'destination', label: '目的地', placeholder: '想去哪里？' },
]
const locations = reactive<Record<Endpoint, Location | null>>({ origin: null, destination: null })
const picker = ref(false), selectedEndpoint = ref<Endpoint>('origin'), radius = ref(3)
const radiusOptions = [1,3,5,10,20].map(value => ({value, label: `${value} 公里内`}))
function readPoint(endpoint: Endpoint): Location | null {
  const lng = route.query[endpoint + '_lng'], lat = route.query[endpoint + '_lat']
  if (typeof lng !== 'string' || typeof lat !== 'string' || !lng.trim() || !lat.trim()) return null
  const longitude = Number(lng), latitude = Number(lat)
  if (!Number.isFinite(longitude) || !Number.isFinite(latitude) || Math.abs(longitude)>180 || Math.abs(latitude)>90) return null
  return {longitude, latitude, address: '', poi_id:null, adcode:null, source:'map', coordinate_system:'gcj02'}
}
function changeName(endpoint: Endpoint, value: string) { filters[endpoint]=value; locations[endpoint]=null }
function selectPoint(name: string, location: Location | null) { filters[selectedEndpoint.value]=name; locations[selectedEndpoint.value]=location }
const scope = ref('published'), page = ref(1), busy = ref(false), error = ref('')
const result = ref<Page<Ride>>({ items: [], total: 0, page: 1, page_size: 12 })
let revision = 0
async function load() {
  const version = ++revision
  filters.origin = String(route.query.origin || '').slice(0,80)
  filters.destination = String(route.query.destination || '').slice(0,80)
  locations.origin = readPoint('origin'); locations.destination = readPoint('destination')
  radius.value = [1,3,5,10,20].includes(Number(route.query.radius_km)) ? Number(route.query.radius_km) : 3
  filters.date = /^\d{4}-\d{2}-\d{2}$/.test(String(route.query.date)) ? String(route.query.date) : ''
  filters.available = route.query.available === '1'
  scope.value = route.query.scope === 'participating' ? 'participating' : 'published'
  page.value = Math.min(100000, Math.max(1, Math.floor(Number(route.query.page) || 1)))
  busy.value = true; error.value = ''
  try {
    const data = await ridesApi.list(props.mine ? { scope: scope.value, page: page.value } : {
      origin: filters.origin, destination: filters.destination, departure_date: filters.date || undefined,
      available_only: filters.available, page: page.value,
      origin_lng: locations.origin?.longitude, origin_lat: locations.origin?.latitude,
      destination_lng: locations.destination?.longitude, destination_lat: locations.destination?.latitude, radius_km: radius.value,
    }, props.mine)
    if (version === revision) result.value = data
  } catch(e) { if (version === revision) error.value = e instanceof Error ? e.message : '加载失败' }
  finally { if (version === revision) busy.value = false }
}
function search(p = 1) {
  const query = props.mine ? { scope: scope.value, page: String(p) } : {
    origin: filters.origin || undefined, destination: filters.destination || undefined, date: filters.date || undefined,
    available: filters.available ? '1' : undefined, page: String(p),
    origin_lng: locations.origin?.longitude.toString(), origin_lat: locations.origin?.latitude.toString(),
    destination_lng: locations.destination?.longitude.toString(), destination_lat: locations.destination?.latitude.toString(),
    radius_km: locations.origin || locations.destination ? String(radius.value) : undefined,
  }
  const target = router.resolve({ path: route.path, query }).fullPath
  if (target === route.fullPath) void load(); else void router.push({ query })
}
function reset() { Object.assign(filters, { origin:'', destination:'', date:'', available:false }); locations.origin=null; locations.destination=null; radius.value=3; search() }
watch(() => route.fullPath, load, { immediate: true })
</script>
<template>
 <AppContainer><main class="ride-page">
  <p class="eyebrow">CAMPUS RIDE · 一起出发</p>
  <PageHeader :title="mine ? '我的拼车' : '校园拼车'" :description="mine ? '每一次出发，都在这里。' : '寻找时间与路线相近的同学，让下一段路有人同行。'">
   <template #actions><div class="ride-actions"><RouterLink :to="mine ? '/ride' : '/ride/mine'"><NButton>{{ mine ? '寻找同行' : '我的拼车' }}</NButton></RouterLink><RouterLink to="/ride/new"><NButton type="primary">发布拼车</NButton></RouterLink></div></template>
  </PageHeader>
  <div v-if="!mine" class="ride-intro">同一个目的地，多一份陪伴。选好集合地点，约定出发时间，让同行更简单。</div>
  <NTabs v-if="mine" v-model:value="scope" type="line" style="margin-bottom:24px" @update:value="search(1)"><NTab name="published">我发布的</NTab><NTab name="participating">我参与的</NTab></NTabs>
  <NCard v-else><form @submit.prevent="search(1)"><div class="ride-filters">
    <div v-for="endpoint in endpoints" :key="endpoint.key" class="ride-field"><label :for="`ride-${endpoint.key}-search`">{{endpoint.label}}</label><div class="ride-place-input"><NInput :value="filters[endpoint.key]" @update:value="value => changeName(endpoint.key,value)" :maxlength="80" :placeholder="endpoint.placeholder" :input-props="{id:`ride-${endpoint.key}-search`}" /><NButton :aria-label="`地图选择${endpoint.label}`" @click="selectedEndpoint=endpoint.key;picker=true">地图选点</NButton></div><p class="ride-address">{{locations[endpoint.key] ? '已选地图位置 · 按附近距离查找' : '手动输入按名称查找'}}</p></div>
    <div><label for="ride-date-search">出发日期 · 北京时间</label><input id="ride-date-search" v-model="filters.date" type="date" class="ride-date" /></div>
    <div class="ride-actions"><NButton attr-type="submit" type="primary">查找同行</NButton><NButton quaternary @click="reset">重置</NButton></div>
  </div><div v-if="locations.origin || locations.destination" class="ride-search-radius"><label for="ride-radius">附近范围</label><NSelect v-model:value="radius" :options="radiusOptions" :input-props="{id:'ride-radius'}" style="width:140px"/><span class="ride-muted">选点按直线距离筛选，不限制地点名称；两端选点需同时满足。未标地图位置的行程不会纳入距离结果。</span></div></form></NCard>
  <div class="ride-filter-bottom"><span class="ride-muted">{{ busy ? '正在寻找同行…' : `共 ${result.total} 条行程` }}</span><NCheckbox v-if="!mine" v-model:checked="filters.available" @update:checked="search(1)">只看有空位</NCheckbox></div>
  <NAlert v-if="error" type="error" class="ride-error">{{ error }} <NButton text @click="load">重新加载</NButton></NAlert>
  <div v-if="busy" class="ride-grid"><NCard v-for="n in 2" :key="n"><NSkeleton text :repeat="5" /></NCard></div>
  <div v-else-if="!error && result.items.length" class="ride-grid"><RideCard v-for="ride in result.items" :key="ride.id" :ride="ride" :return-to="route.fullPath" /></div>
  <NCard v-else-if="!error"><div class="ride-empty"><h2>{{ mine ? '还没有相关行程' : '暂时没有合适的同行' }}</h2><p>{{ mine ? '去寻找一段同行，或发起自己的邀约。' : '换个时间或地点试试，也可以先发起邀约。' }}</p><RouterLink to="/ride/new"><NButton type="primary">发布拼车</NButton></RouterLink></div></NCard>
  <div v-if="!error && result.total > 12" class="ride-pagination"><NPagination :page="page" :item-count="result.total" :page-size="12" :page-slot="5" @update:page="search" /></div>
  <LocationPicker v-model:show="picker" :title="selectedEndpoint==='origin' ? '查找的出发地' : '查找的目的地'" :name="filters[selectedEndpoint]" :location="locations[selectedEndpoint]" :max-length="80" @select="selectPoint" />
 </main></AppContainer>
</template>
