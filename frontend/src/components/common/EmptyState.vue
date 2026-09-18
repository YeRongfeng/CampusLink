<script setup lang="ts">
import { NEmpty } from 'naive-ui'
withDefaults(defineProps<{ description?: string }>(), { description: '功能开发中' })
</script>
<template><div class="empty-panel"><NEmpty :description="description"><template #extra><slot /></template></NEmpty></div></template>
