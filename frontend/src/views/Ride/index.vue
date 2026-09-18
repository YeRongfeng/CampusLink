<script setup lang="ts">
import { NCard } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import EmptyState from '../../components/common/EmptyState.vue'
</script>
<template>
  <AppContainer><main class="py-8">
    <PageHeader title="校园拼车" description="寻找时间与路线相近的同学。" />
    <NCard><EmptyState /></NCard>
  </main></AppContainer>
</template>
