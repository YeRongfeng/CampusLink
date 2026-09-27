<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NAlert, NButton, NCard, NInput, NModal, NSelect, NSkeleton, NTag } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import UserAvatar from '../../components/common/UserAvatar.vue'
import RideMap from './components/RideMap.vue'
import { useAuthStore } from '../../stores/auth'
import { ridesApi } from './api'
import { contactNames, contactOptions, formatTime, statusNames } from './types'
import type { Contact, Contacts, Membership, RideDetail } from './types'
import './ride.css'
const route=useRoute(),auth=useAuthStore()
const ride=ref<RideDetail>(),member=ref<Membership>(),contacts=ref<Contacts>(),loading=ref(true),busy=ref(false),error=ref(''),contactError=ref(''),notice=ref('')
const joinOpen=ref(false),joinError=ref(''),confirmAction=ref<'leave'|'cancel'|'complete'|null>(null)
const contact=reactive<Contact>({contact_type:'wechat',contact_value:''})
const back=computed(()=>{const value=String(route.query.from||'');return /^\/ride(?:\/mine)?(?:\?|$)/.test(value)?value:'/ride'})
const actionTitle=computed(()=>({leave:'退出拼车',cancel:'取消行程',complete:'标记完成'}[confirmAction.value||'leave']))
let revision=0,contactRevision=0,departureTimer:ReturnType<typeof setTimeout>|undefined
const cutoff=ref(false)
function setCutoff(data:RideDetail){clearTimeout(departureTimer);cutoff.value=false;const delay=Date.parse(data.departure_at)-Date.parse(data.server_time);if(data.status==='scheduled'&&delay>0&&delay<2147483647)departureTimer=setTimeout(()=>{cutoff.value=true;void load()},delay+100)}
async function load() {
 const version=++revision;contactRevision++;ride.value=undefined;contacts.value=undefined;member.value=undefined;contactError.value='';loading.value=true;error.value='';clearTimeout(departureTimer)
 try {
  const data=await ridesApi.detail(Number(route.params.id));if(version!==revision)return
  ride.value=data;setCutoff(data)
  if(auth.isAuthenticated){const relation=await ridesApi.membership(data.id);if(version===revision)member.value=relation}
 }catch(e){if(version===revision)error.value=e instanceof Error?e.message:'行程加载失败'}finally{if(version===revision)loading.value=false}
}
async function loadContacts(){const seq=++contactRevision,version=revision;contactError.value='';try{const data=await ridesApi.contacts(Number(route.params.id));if(seq===contactRevision&&version===revision&&auth.isAuthenticated)contacts.value=data}catch(e){if(seq===contactRevision)contactError.value=e instanceof Error?e.message:'无法获取联系方式'}}
async function join(){if(busy.value)return;joinError.value='';if(contact.contact_value.trim().length<3){joinError.value='请输入至少 3 个字符的联系方式';return}busy.value=true;try{await ridesApi.join(Number(route.params.id),contact);joinOpen.value=false;notice.value='已加入拼车，可以联系发起人确认集合。';await load()}catch(e){joinError.value=e instanceof Error?e.message:'加入失败';await load()}finally{busy.value=false}}
async function act(){if(!confirmAction.value||busy.value)return;busy.value=true;try{await ridesApi.act(Number(route.params.id),confirmAction.value);notice.value='操作已保存';confirmAction.value=null;await load()}catch(e){confirmAction.value=null;await load();error.value=e instanceof Error?e.message:'操作失败'}finally{busy.value=false}}
watch(()=>[route.params.id,auth.token],()=>{joinOpen.value=false;confirmAction.value=null;contacts.value=undefined;member.value=undefined;contact.contact_value='';notice.value=route.query.saved?'拼车已保存':'';void load()},{immediate:true})
onBeforeUnmount(()=>{revision++;contactRevision++;clearTimeout(departureTimer)})
</script>
<template>
 <AppContainer><main class="ride-page">
  <PageHeader title="同行详情" description="约定好时间和地点，一起出发。"><template #actions><RouterLink :to="back"><NButton quaternary>返回行程列表</NButton></RouterLink></template></PageHeader>
  <NAlert v-if="notice" type="success" class="ride-error" closable @close="notice=''">{{notice}}</NAlert>
  <NAlert v-if="error" type="error" class="ride-error">{{error}} <NButton text @click="load">重新加载</NButton></NAlert>
  <NSkeleton v-if="loading" text :repeat="8" />
  <div v-else-if="ride" class="ride-detail-grid">
   <div><NCard class="ride-section"><NTag :bordered="false" :type="ride.display_status==='open'?'success':'default'">{{statusNames[ride.display_status]}}</NTag><h2 class="ride-detail-route">{{ride.origin}}<span>→</span>{{ride.destination}}</h2><p style="font-size:18px;font-weight:600">{{formatTime(ride.departure_at)}}</p><span class="ride-muted">北京时间 · 发起人默认同行</span><dl class="ride-detail-list"><div><dt>集合地点</dt><dd>{{ride.meeting_point}}<p v-if="ride.meeting_location?.address" class="ride-address">{{ride.meeting_location.address}}</p><p v-if="ride.meeting_note" class="ride-note">{{ride.meeting_note}}</p></dd></div><div v-if="ride.origin_location?.address"><dt>出发地详细地址</dt><dd>{{ride.origin_location.address}}</dd></div><div v-if="ride.destination_location?.address"><dt>目的地详细地址</dt><dd>{{ride.destination_location.address}}</dd></div><div><dt>预计费用</dt><dd>{{ride.estimated_cost===null?'费用协商':`每人预计 ¥${ride.estimated_cost}`}}<p class="ride-muted">实际费用由同行同学线下协商。</p></dd></div></dl><RideMap :key="ride.id" :ride="ride"/></NCard><NCard title="同行备注"><p class="ride-note">{{ride.note||'发起人还没有补充备注。'}}</p></NCard></div>
   <div><NCard class="ride-section"><div class="ride-people"><UserAvatar :user="ride.owner" :size="44"/><div><strong>{{ride.owner.nickname}}</strong><div class="ride-muted">行程发起人</div></div></div><p style="font-size:16px">还可加入 <strong style="font-size:32px;color:var(--primary)">{{ride.remaining_seats}}</strong> 人</p><p class="ride-muted">已加入 {{ride.joined_count}} / 招募 {{ride.recruit_seats}} 人（不含发起人）</p>
    <template v-if="!auth.isAuthenticated"><RouterLink :to="{path:'/login',query:{redirect:route.fullPath}}"><NButton type="primary" block>登录后加入</NButton></RouterLink></template>
    <template v-else-if="member"><NTag v-if="member.role==='owner'" :bordered="false">你发起的行程</NTag><NTag v-else-if="member.member_status" :bordered="false">{{member.member_status==='joined'?'你已加入':'你已退出'}}</NTag><div class="ride-actions" style="margin-top:18px"><NButton v-if="member.can_join&&!cutoff" type="primary" :disabled="busy" @click="joinOpen=true">加入拼车</NButton><NButton v-if="member.can_leave&&!cutoff" :disabled="busy" @click="confirmAction='leave'">退出拼车</NButton><RouterLink v-if="member.can_edit&&!cutoff" :to="`/ride/${ride.id}/edit`"><NButton :disabled="busy">编辑行程</NButton></RouterLink><NButton v-if="member.can_cancel&&!cutoff" :disabled="busy" @click="confirmAction='cancel'">取消行程</NButton><NButton v-if="member.can_complete" type="primary" :disabled="busy" @click="confirmAction='complete'">标记完成</NButton></div><p v-if="!member.can_join&&member.role==='visitor'" class="ride-muted">{{statusNames[ride.display_status]}}，暂时不能加入。</p></template>
   </NCard><NCard v-if="member && member.role!=='visitor' && ride.status!=='cancelled'" :title="member.role==='owner'?'同行联系':'联系发起人'"><NAlert v-if="contactError" type="warning">{{contactError}}</NAlert><NButton v-if="!contacts" @click="loadContacts">查看联系方式</NButton><template v-else><div class="ride-people"><UserAvatar :user="contacts.owner" :size="32"/><div><strong>{{contacts.owner.nickname}}</strong><div>{{contactNames[contacts.owner.contact_type]}}：{{contacts.owner.contact_value}}</div></div></div><template v-if="member.role==='owner'"><p class="ride-muted">已加入的同学</p><div v-for="person in contacts.active_members" :key="person.id" class="ride-people"><UserAvatar :user="person" :size="32"/><div><strong>{{person.nickname}}</strong><div>{{contactNames[person.contact_type]}}：{{person.contact_value}}</div></div></div><p v-if="!contacts.active_members.length" class="ride-muted">暂时还没有同学加入。</p></template><NButton text style="margin-top:12px" @click="load">刷新行程及联系权限</NButton></template></NCard></div>
  </div>
  <NModal v-model:show="joinOpen" preset="card" title="加入这次同行" style="width:min(440px,94vw)" :mask-closable="!busy" :closable="!busy"><NAlert v-if="joinError" type="error">{{joinError}}</NAlert><p class="ride-muted">加入后占用 1 个名额。以下联系方式仅提供给发起人，方便确认集合事宜。</p><form @submit.prevent="join"><label>联系类型</label><NSelect v-model:value="contact.contact_type" :disabled="busy" :options="contactOptions" style="margin:8px 0 16px"/><label for="join-contact">联系方式</label><NInput v-model:value="contact.contact_value" :disabled="busy" :maxlength="64" :input-props="{id:'join-contact'}" style="margin:8px 0 20px"/><NButton type="primary" attr-type="submit" block :loading="busy">确认加入</NButton></form></NModal>
  <NModal :show="Boolean(confirmAction)" preset="dialog" :title="actionTitle" :positive-text="actionTitle" negative-text="暂不操作" :loading="busy" :mask-closable="!busy" :closable="!busy" @positive-click="act" @negative-click="confirmAction=null" @close="confirmAction=null"><p>{{confirmAction==='cancel'?'取消后行程将停止报名，已加入的同学会在历史中看到取消状态。':confirmAction==='complete'?'确认这条同行邀约已结束？完成后不能恢复。':'退出后将释放名额，并无法继续查看发起人的联系方式。'}}</p></NModal>
 </main></AppContainer>
</template>
