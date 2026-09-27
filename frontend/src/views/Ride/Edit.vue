<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NInput, NInputNumber, NSelect, NSkeleton } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import LocationPicker from './components/LocationPicker.vue'
import { ridesApi } from './api'
import { contactOptions, toBeijingInput } from './types'
import type { Location, RideWrite } from './types'
import './ride.css'
const route=useRoute(),router=useRouter(),id=route.params.id ? Number(route.params.id) : undefined
const busy=ref(false),loading=ref(Boolean(id)),error=ref(''),loadFailed=ref(false),saved=ref(false)
const model=reactive<RideWrite>({origin:'',destination:'',meeting_point:'',origin_location:null,destination_location:null,meeting_location:null,meeting_note:'',departure_at:'',recruit_seats:3,estimated_cost:null,contact_type:'wechat',contact_value:'',note:''})
const departure=ref(''),cost=ref<number|null>(null),baseline=ref('')
const snapshot=()=>JSON.stringify([model,departure.value,cost.value])
const dirty=computed(()=>Boolean(baseline.value)&&snapshot()!==baseline.value&&!saved.value)
const fields=[{key:'origin',location:'origin_location',label:'出发地',max:80},{key:'destination',location:'destination_location',label:'目的地',max:80},{key:'meeting_point',location:'meeting_location',label:'集合地点',max:160}] as const
type Field = typeof fields[number]
const selectedField=ref<Field>(fields[0]),picker=ref(false),meetingHint=ref(false)
function changeName(field:Field,value:string) {model[field.key]=value;model[field.location]=null;if(field.key==='origin'&&model.meeting_point)meetingHint.value=true}
function choose(field:Field) {selectedField.value=field;picker.value=true}
function selected(name:string,location:Location|null) {const field=selectedField.value;model[field.key]=name;model[field.location]=location;if(field.key==='origin'&&model.meeting_point)meetingHint.value=true;if(field.key==='meeting_point')meetingHint.value=false}
async function load() {
 loading.value=Boolean(id);error.value='';loadFailed.value=false
 if(id) try {
   const [ride,member]=await Promise.all([ridesApi.detail(id),ridesApi.membership(id)])
   if(!member.can_edit)throw new Error('仅本人发布、尚未出发且无人加入的行程可以编辑')
   const contacts=await ridesApi.contacts(id)
   for(const field of fields){model[field.key]=ride[field.key];model[field.location]=ride[field.location]}
   Object.assign(model,{meeting_note:ride.meeting_note,note:ride.note,recruit_seats:ride.recruit_seats,contact_type:contacts.owner.contact_type,contact_value:contacts.owner.contact_value})
   departure.value=toBeijingInput(ride.departure_at);cost.value=ride.estimated_cost===null?null:Number(ride.estimated_cost)
 }catch(e){error.value=e instanceof Error?e.message:'无法加载行程';loadFailed.value=true}
 loading.value=false;baseline.value=snapshot()
}
async function submit() {
 if(busy.value)return
 error.value=''
 for(const field of fields)if(model[field.key].trim().length<2){error.value=`请填写至少 2 个字符的${field.label}`;return}
 const time=Date.parse(departure.value+':00+08:00')
 if(!Number.isFinite(time)||time<=Date.now()||time>Date.now()+90*86400000){error.value='请选择未来 90 天内的出发时间（北京时间）';return}
 if(!Number.isInteger(model.recruit_seats)||model.recruit_seats<1||model.recruit_seats>6){error.value='招募人数需为 1–6 人';return}
 if(model.contact_value.trim().length<3){error.value='请填写有效的联系方式，至少 3 个字符';return}
 const a=model.origin_location,b=model.destination_location
 if(a&&b ? a.longitude===b.longitude&&a.latitude===b.latitude : model.origin.trim()===model.destination.trim()&&(a?.address||'')===(b?.address||'')){error.value='出发地与目的地不能是同一地点';return}
 busy.value=true
 try {
  const result=await ridesApi.save({...model,departure_at:new Date(time).toISOString(),estimated_cost:cost.value===null?null:cost.value.toFixed(2)},id)
  saved.value=true;await router.push({path:`/ride/${result.id}`,query:{saved:'1',from:'/ride/mine'}})
 }catch(e){error.value=(e instanceof Error?e.message:'保存失败')+'。若网络中断，请先在“我的拼车”确认是否已保存。'}finally{busy.value=false}
}
function leaving(event:BeforeUnloadEvent){if(dirty.value){event.preventDefault();event.returnValue=''}}
onMounted(()=>{void load();window.addEventListener('beforeunload',leaving)})
onBeforeUnmount(()=>window.removeEventListener('beforeunload',leaving))
onBeforeRouteLeave(()=>!dirty.value||window.confirm('尚有未保存的内容，确定离开吗？'))
</script>
<template>
 <AppContainer><main class="ride-page ride-form">
  <PageHeader :title="id ? '编辑拼车' : '发布拼车'" description="把出发的计划，变成一次同行。"><template #actions><RouterLink to="/ride"><NButton quaternary>返回大厅</NButton></RouterLink></template></PageHeader>
  <NAlert v-if="error" type="error" class="ride-error" aria-live="polite">{{error}} <NButton v-if="loadFailed" text @click="load">重新加载</NButton></NAlert>
  <NSkeleton v-if="loading" text :repeat="8" />
  <form v-else-if="!loadFailed" @submit.prevent="submit">
   <NCard class="ride-section"><h2>路线与时间</h2><div class="ride-form-grid">
    <div v-for="field in fields" :key="field.key" class="ride-field" :class="{full:field.key==='meeting_point'}"><label :for="`ride-${field.key}`">{{field.label}} *</label><div class="ride-place-input"><NInput :value="model[field.key]" :maxlength="field.max" :disabled="busy" :placeholder="`输入${field.label}，或在地图上选择`" :input-props="{id:`ride-${field.key}`}" @update:value="value=>changeName(field,value)"/><NButton :disabled="busy" @click="choose(field)">地图选点</NButton></div><p v-if="model[field.location]" class="ride-address">已选地图位置 · {{model[field.location]?.address || '可在地图中查看'}}</p></div>
    <div class="ride-field full"><label for="ride-meeting-note">集合补充说明</label><NInput v-model:value="model.meeting_note" :disabled="busy" :maxlength="200" placeholder="例如：南门右侧便利店门口" :input-props="{id:'ride-meeting-note'}"/><p v-if="meetingHint" class="ride-address">出发地已更改，请确认集合地点是否仍然合适。</p></div>
    <div class="ride-field full"><label for="ride-departure">出发时间 * · 北京时间</label><input id="ride-departure" v-model="departure" class="ride-date" type="datetime-local" required :disabled="busy" /></div>
   </div></NCard>
   <NCard class="ride-section"><h2>人数与费用</h2><div class="ride-form-grid"><div class="ride-field"><label for="ride-seats">招募人数 *</label><NInputNumber v-model:value="model.recruit_seats" :disabled="busy" :min="1" :max="6" :precision="0" :input-props="{id:'ride-seats'}"/><p class="ride-muted">除你之外，还希望有几位同学加入？</p></div><div class="ride-field"><label for="ride-cost">每人预计分摊（元）</label><NInputNumber v-model:value="cost" :disabled="busy" :min="0" :max="9999.99" :precision="2" placeholder="留空则费用协商" :input-props="{id:'ride-cost'}"/><p class="ride-muted">仅为预计费用，实际金额由同行同学线下协商。</p></div></div></NCard>
   <NCard class="ride-section"><h2>联系方式与备注</h2><div class="ride-form-grid"><div class="ride-field"><label>联系类型 *</label><NSelect v-model:value="model.contact_type" :disabled="busy" :options="contactOptions" aria-label="联系类型" /></div><div class="ride-field"><label for="ride-contact">联系方式 *</label><NInput v-model:value="model.contact_value" :disabled="busy" :maxlength="64" :input-props="{id:'ride-contact'}" placeholder="填写方便联系你的账号或号码" /></div><div class="ride-field full"><label for="ride-note">同行备注</label><NInput v-model:value="model.note" :disabled="busy" type="textarea" :maxlength="500" show-count :autosize="{minRows:3,maxRows:6}" :input-props="{id:'ride-note'}" placeholder="行李、集合要求，或想提前告诉同学的话" /></div></div><p class="ride-muted">联系方式仅对已加入的同学开放。发布后，所选行程地点及集合说明将公开展示。</p></NCard>
   <div class="ride-actions" style="justify-content:flex-end"><RouterLink to="/ride/mine"><NButton :disabled="busy">我的拼车</NButton></RouterLink><NButton attr-type="submit" type="primary" size="large" :loading="busy">{{id?'保存修改':'发布拼车'}}</NButton></div>
  </form>
  <LocationPicker v-model:show="picker" :title="selectedField.label" :name="model[selectedField.key]" :location="model[selectedField.location]" :center="model.origin_location" :max-length="selectedField.max" @select="selected" />
 </main></AppContainer>
</template>
