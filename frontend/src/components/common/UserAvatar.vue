<script setup lang="ts">
import { NAvatar } from 'naive-ui'
import type { User } from '../../types/user'
withDefaults(defineProps<{ user: User | null; size?: number }>(), { size: 48 })
</script>
<template>
  <NAvatar v-if="user?.avatar" :size="size" :src="user.avatar" round :img-props="{ alt: '用户头像' }">
    <template #fallback>{{ user.nickname.slice(0, 1) }}</template>
  </NAvatar>
  <NAvatar v-else :size="size" round>{{ user?.nickname.slice(0, 1) || '同' }}</NAvatar>
</template>
