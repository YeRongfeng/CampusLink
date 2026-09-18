<script setup lang="ts">
defineProps<{ title: string; description?: string }>()
</script>
<template>
  <div class="page-heading mb-6 flex flex-wrap items-center justify-between gap-4">
    <div><h1 class="m-0 text-2xl font-semibold">{{ title }}</h1><p v-if="description" class="mb-0 mt-2 text-[var(--text-secondary)]">{{ description }}</p></div>
    <slot name="actions" />
  </div>
</template>
