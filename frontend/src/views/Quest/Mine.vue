<script setup lang="ts">
import { NCard } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import EmptyState from '../../components/common/EmptyState.vue'
</script>
<template>
  <AppContainer><main class="py-8">
    <PageHeader title="我的悬赏" description="" />
    <NCard><EmptyState /></NCard>
  </main></AppContainer>
</template>
