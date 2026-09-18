<script setup lang="ts">
import { NCard } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import EmptyState from '../../components/common/EmptyState.vue'
</script>
<template>
  <AppContainer><main class="py-8">
    <PageHeader title="CampusQuest 校园悬赏" description="发布校园互助需求，让顺路或擅长的人帮你完成。" />
    <NCard><EmptyState /></NCard>
  </main></AppContainer>
</template>
