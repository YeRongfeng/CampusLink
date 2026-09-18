<script setup lang="ts">
import { NCard } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import EmptyState from '../../components/common/EmptyState.vue'
</script>
<template>
  <AppContainer><main class="py-8">
    <PageHeader title="校园二手书" description="让闲置教材和参考书继续流转。" />
    <NCard><EmptyState /></NCard>
  </main></AppContainer>
</template>
