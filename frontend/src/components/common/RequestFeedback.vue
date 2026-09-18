<script setup lang="ts">
import { onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import { setErrorNotifier } from '../../api/request'

const message = useMessage()
setErrorNotifier((text) => message.error(text))
onUnmounted(() => setErrorNotifier(() => {}))
</script>

<template><slot /></template>
