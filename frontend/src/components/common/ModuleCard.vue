<script setup lang="ts">
defineProps<{ title: string; description: string; to: string; label?: string; number?: string }>()
</script>
<template>
  <RouterLink :to="to" class="module-card">
    <div class="module-card-top"><span>{{ label }}</span><span class="module-number">{{ number }}</span></div>
    <h3>{{ title }}</h3><p>{{ description }}</p>
    <span class="module-card-action">进入{{ title }} <span aria-hidden="true">→</span></span>
  </RouterLink>
</template>
