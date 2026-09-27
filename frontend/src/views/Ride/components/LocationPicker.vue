<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { NAlert, NButton, NInput, NModal, NSpin } from 'naive-ui'
import { loadMap, mapUnavailable, sdkCall, locationOf } from '../amap'
import type { AMapObject, AMapSDK } from '../amap'
import type { Location } from '../types'
const props = defineProps<{ title: string; name: string; location: Location | null; center?: Location | null; maxLength?: number }>()
const emit = defineEmits<{ select: [name: string, location: Location | null] }>()
const show = defineModel<boolean>('show', { default: false })
const canvas = ref<HTMLDivElement>(), loading = ref(false), working = ref(false), error = ref('')
const keyword = ref(''), city = ref(''), draftName = ref(''), draftAddress = ref(''), selected = ref<Location | null>(null)
const results = ref<AMapObject[]>([])
let sdk: AMapSDK, map: AMapObject, marker: AMapObject, session = 0, selection = 0, searching = 0
let debounce: ReturnType<typeof setTimeout> | undefined
function destroy() { session++; selection++; searching++; clearTimeout(debounce); map?.destroy(); map=null; marker=null; results.value=[] }
async function initialize() {
  destroy(); const current = session
  loading.value=true; working.value=false; error.value=''; keyword.value=''
  draftName.value=props.name; draftAddress.value=props.location?.address || ''; selected.value=props.location ? {...props.location} : null
  try {
    await nextTick(); sdk=await loadMap()
    if (!show.value || current!==session || !canvas.value) return
    const center=props.location || props.center
    map=new sdk.Map(canvas.value, {zoom:center ? 15 : 4, center:center ? [center.longitude,center.latitude] : [104,35], viewMode:'2D'})
    map.on('click',(event: AMapObject)=>void pickPoint(event.lnglat,'map'))
    if (props.location) placeMarker(props.location)
  } catch { if(current===session) error.value=mapUnavailable }
  finally { if(current===session) loading.value=false }
}
function placeMarker(point: Location) {
  if (!map) return
  if (!marker) {
    marker=new sdk.Marker({draggable:true}); map.add(marker)
    marker.on('dragend',(event: AMapObject)=>void pickPoint(event.lnglat,'map'))
  }
  marker.setPosition([point.longitude,point.latitude]); map.setZoomAndCenter(16,[point.longitude,point.latitude])
}
async function pickPoint(position: AMapObject, source: Location['source']) {
  const current=session, seq=++selection; error.value=''; working.value=true
  try {
    const point=locationOf(position,source); selected.value=point; draftName.value='地图选定地点'; draftAddress.value=''; placeMarker(point)
    const data=await sdkCall(cb=>new sdk.Geocoder().getAddress([point.longitude,point.latitude],cb))
    if(current!==session || seq!==selection) return
    point.address=String(data.regeocode?.formattedAddress || '').slice(0,300)
    point.adcode=/^\d{6}$/.test(data.regeocode?.addressComponent?.adcode || '') ? data.regeocode.addressComponent.adcode : null
    selected.value=point; draftAddress.value=point.address
    draftName.value=point.address.slice(0,props.maxLength || 80) || '地图选定地点'
  } catch(e) { if(current===session && seq===selection) error.value=e instanceof Error ? e.message : '地址获取失败，可补充地点名称' }
  finally { if(current===session && seq===selection) working.value=false }
}
async function search() {
  const current=session, seq=++searching; results.value=[]
  if(!map || keyword.value.trim().length<2) return
  try {
    error.value=''
    const data=await sdkCall(cb=>new sdk.AutoComplete({city:city.value || '全国',citylimit:false}).search(keyword.value.trim(),cb))
    if(current===session && seq===searching) { results.value=data.tips || []; if(!results.value.length) error.value='没有匹配地点，请换关键词或在地图选点' }
  } catch(e) { if(current===session && seq===searching) error.value=e instanceof Error ? e.message : mapUnavailable }
}
function scheduleSearch(){ searching++; clearTimeout(debounce); debounce=setTimeout(search,300) }
async function choose(tip: AMapObject) {
  const current=session, seq=++selection; working.value=true; error.value=''
  try {
    let poi=tip
    if (!tip.location || typeof tip.location === 'string') {
      if (!tip.id) throw new Error('请选择具体地点，或在地图上点击位置')
      const data=await sdkCall(cb=>new sdk.PlaceSearch().getDetails(tip.id,cb))
      poi=data.poiList?.pois?.[0]
    }
    const point=locationOf(poi?.location,'poi',String((poi?.district || '') + (typeof poi?.address === 'string' ? poi.address : '')),poi?.id,poi?.adcode)
    if(current!==session || seq!==selection) return
    selected.value=point; draftName.value=String(poi.name || tip.name).slice(0,props.maxLength || 80); draftAddress.value=point.address; results.value=[]; placeMarker(point)
  } catch(e) { if(current===session && seq===selection) error.value=e instanceof Error ? e.message : mapUnavailable }
  finally { if(current===session && seq===selection) working.value=false }
}
async function locate() {
  const current=session, seq=++selection; working.value=true; error.value=''
  try {
    const data=await sdkCall(cb=>new sdk.Geolocation({enableHighAccuracy:true,timeout:8000,convert:true,showButton:false,showMarker:false,panToLocation:false}).getCurrentPosition(cb))
    if(current!==session || seq!==selection) return
    await pickPoint(data.position,'geolocation')
  } catch { if(current===session && seq===selection) error.value='定位未成功。请检查浏览器权限，或搜索、点击地图选择地点。' }
  finally { if(current===session && seq===selection) working.value=false }
}
function confirm() {
  if(draftName.value.trim().length<2) {error.value='请输入至少 2 个字符的地点名称';return}
  emit('select',draftName.value.trim(),selected.value ? {...selected.value,address:draftAddress.value.trim()} : null)
  show.value=false
}
watch(show,value=>{ if(value) void initialize(); else destroy() })
onBeforeUnmount(destroy)
</script>
<template>
 <NModal v-model:show="show" preset="card" :title="`选择${title}`" class="ride-map-modal" :mask-closable="false">
  <NAlert v-if="error" type="warning" style="margin-bottom:14px">{{error}} <NButton v-if="!map && !loading" text @click="initialize">重试地图</NButton></NAlert>
  <div class="ride-actions"><NInput v-model:value="city" placeholder="搜索城市（可选）" aria-label="搜索城市" style="width:170px" @update:value="scheduleSearch" /><NInput v-model:value="keyword" placeholder="输入学校、车站或地点名称" aria-label="搜索地点" style="flex:1;min-width:180px" @update:value="scheduleSearch" @keyup.enter="search" /></div>
  <div v-if="results.length" class="ride-map-results"><button v-for="(tip,i) in results" :key="i" class="ride-map-result" :disabled="working" @click="choose(tip)"><strong>{{tip.name}}</strong><br/><span class="ride-muted">{{tip.district}} {{tip.address}}</span></button></div>
  <NSpin :show="loading"><div ref="canvas" class="ride-map-canvas" style="margin-top:14px" /></NSpin>
  <p class="ride-muted">点击“使用当前位置”将请求浏览器定位，并通过高德解析地址，仅用于本次选点。请确认所选地点后再保存。</p>
  <NButton :disabled="!map || working" :loading="working" @click="locate">使用当前位置</NButton>
  <div class="ride-form-grid" style="margin-top:18px"><div class="ride-field"><label for="map-place-name">地点名称</label><NInput v-model:value="draftName" :maxlength="maxLength || 80" :input-props="{id:'map-place-name'}" /></div><div class="ride-field"><label for="map-place-address">详细地址</label><NInput v-model:value="draftAddress" :maxlength="300" :input-props="{id:'map-place-address'}" /></div></div>
  <p class="ride-muted">{{selected ? '已选坐标，可拖动地图标记调整位置。' : '未选地图位置，将保存为手动填写地点。'}}</p>
  <template #footer><div class="ride-actions" style="justify-content:flex-end"><NButton @click="show=false">取消</NButton><NButton type="primary" :disabled="working || loading" @click="confirm">确认地点</NButton></div></template>
 </NModal>
</template>
