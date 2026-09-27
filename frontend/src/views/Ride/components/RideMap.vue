<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref } from 'vue'
import { NAlert, NButton } from 'naive-ui'
import { loadMap, mapUnavailable } from '../amap'
import type { AMapObject } from '../amap'
import type { RideDetail } from '../types'
const props=defineProps<{ride:RideDetail}>()
const canvas=ref<HTMLDivElement>(), shown=ref(false), loading=ref(false), error=ref('')
let map:AMapObject, active=true
async function open() {
 shown.value=true; loading.value=true; error.value=''
 try {
  await nextTick(); const sdk=await loadMap(); if(!active || !canvas.value)return
  map?.destroy(); map=new sdk.Map(canvas.value,{zoom:12,center:[104,35],viewMode:'2D'})
  const entries=[['起点',props.ride.origin_location],['终点',props.ride.destination_location],['集合',props.ride.meeting_location]] as const
  for(const [label,point] of entries) if(point) map.add(new sdk.Marker({position:[point.longitude,point.latitude],label:{content:label,direction:'top'}}))
  map.setFitView(null,false,[40,40,40,40],16)
 } catch {if(active)error.value=mapUnavailable} finally {if(active)loading.value=false}
}
onBeforeUnmount(()=>{active=false;map?.destroy()})
</script>
<template><section v-if="ride.origin_location || ride.destination_location || ride.meeting_location"><NButton :loading="loading" @click="open">{{shown ? '重新加载地图' : '查看地点地图'}}</NButton><NAlert v-if="error" type="warning" style="margin-top:14px">{{error}}</NAlert><div v-if="shown" ref="canvas" class="ride-map-canvas" style="margin-top:16px" /><p v-if="shown" class="ride-muted">标记为发布者确认的地点，请结合集合说明辨认。</p></section></template>
