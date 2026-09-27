<script setup lang="ts">
import { NTag } from 'naive-ui'
import UserAvatar from '../../../components/common/UserAvatar.vue'
import { formatTime, statusNames } from '../types'
import type { Ride } from '../types'
defineProps<{ ride: Ride; returnTo: string }>()
</script>
<template>
  <RouterLink class="ride-card" :to="{ path: `/ride/${ride.id}`, query: { from: returnTo } }">
    <div class="card-top"><span>CAMPUS RIDE</span><NTag round :bordered="false" :type="ride.display_status === 'open' ? 'success' : ride.display_status === 'full' ? 'warning' : 'default'">{{ statusNames[ride.display_status] }}</NTag></div>
    <h2>{{ ride.origin }} <span>→</span> {{ ride.destination }}</h2>
    <p class="departure">{{ formatTime(ride.departure_at) }} <small>北京时间</small></p>
    <p class="ride-muted">集合 · {{ ride.meeting_point }}</p>
    <p v-if="ride.origin_distance_km != null || ride.destination_distance_km != null" class="ride-muted"><span v-if="ride.origin_distance_km != null">出发地距选点约 {{ ride.origin_distance_km }} 公里</span><span v-if="ride.origin_distance_km != null && ride.destination_distance_km != null"> · </span><span v-if="ride.destination_distance_km != null">目的地距选点约 {{ ride.destination_distance_km }} 公里</span>（直线）</p>
    <div class="numbers"><span>还可加入 <strong>{{ ride.remaining_seats }}</strong> 人</span><span>{{ ride.estimated_cost === null ? '费用协商' : `每人预计 ¥${ride.estimated_cost}` }}</span></div>
    <div class="card-footer"><UserAvatar :user="ride.owner" :size="28" /><span>{{ ride.owner.nickname }}</span><NTag v-if="ride.member_status" size="small" :bordered="false">{{ ride.member_status === 'joined' ? '已加入' : '已退出' }}</NTag><b>查看详情 →</b></div>
  </RouterLink>
</template>
<style scoped>
.ride-card{display:block;padding:24px;border:1px solid var(--border);background:white;border-radius:12px;color:var(--text-primary);text-decoration:none;transition:box-shadow .2s,border-color .2s;min-width:0}.ride-card:hover{border-color:#a4cbb0;box-shadow:0 8px 26px #2847320b}.card-top{display:flex;justify-content:space-between;gap:12px;align-items:center}.card-top>span{font-size:10px;letter-spacing:2px;color:#819187}h2{font-size:22px;line-height:1.6;margin:22px 0 12px;overflow-wrap:anywhere}h2 span{color:var(--primary)}.departure{font-weight:600;font-size:15px}.departure small{font-weight:400;font-size:11px;color:var(--text-secondary)}.numbers{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:13px;margin:20px 0}.numbers strong{font-size:22px;color:var(--primary)}.card-footer{display:flex;align-items:center;gap:10px;border-top:1px solid var(--border);padding-top:18px;font-size:12px}.card-footer>span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.card-footer b{margin-left:auto;white-space:nowrap;color:var(--primary);font-weight:500}
</style>
