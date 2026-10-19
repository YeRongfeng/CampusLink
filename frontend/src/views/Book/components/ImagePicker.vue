<script setup lang="ts">
import { ref } from 'vue'
import { NAlert } from 'naive-ui'
import { uploadImage } from '../../../api/file'

const props = withDefaults(defineProps<{ modelValue: string[]; max?: number }>(), { max: 6 })
const emit = defineEmits<{ 'update:modelValue': [string[]] }>()
const busy = ref(false)
const error = ref('')

function setAsCover(index: number) {
  const next = [...props.modelValue]
  const [picked] = next.splice(index, 1)
  next.unshift(picked)
  emit('update:modelValue', next)
}
function remove(index: number) {
  emit('update:modelValue', props.modelValue.filter((_, i) => i !== index))
}
async function addFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  input.value = ''
  if (!files.length || busy.value) return
  error.value = ''
  const room = props.max - props.modelValue.length
  if (room <= 0) { error.value = `最多上传 ${props.max} 张图片`; return }
  const picked = files.slice(0, room)
  busy.value = true
  try {
    const uploaded: string[] = []
    for (const file of picked) {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
        error.value = '请选择不超过 5 MB 的 JPEG、PNG 或 WebP 图片'
        continue
      }
      const { url } = await uploadImage(file)
      uploaded.push(url)
    }
    if (uploaded.length) emit('update:modelValue', [...props.modelValue, ...uploaded])
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : '图片上传失败，请重试'
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <div>
    <NAlert v-if="error" type="error" style="margin-bottom:12px" closable @close="error = ''">{{ error }}</NAlert>
    <div class="book-image-picker">
      <div v-for="(url, index) in modelValue" :key="url" class="book-image-item">
        <img :src="url" :alt="`书籍图片 ${index + 1}`" />
        <span v-if="index === 0" class="book-image-cover-badge">封面</span>
        <div class="book-image-actions">
          <button v-if="index !== 0" type="button" @click="setAsCover(index)">设为封面</button>
          <button type="button" @click="remove(index)">删除</button>
        </div>
      </div>
      <label v-if="modelValue.length < max" class="book-image-add" :class="{ busy }">
        <input type="file" accept="image/jpeg,image/png,image/webp" multiple class="hidden" :disabled="busy" @change="addFiles" />
        <span v-if="busy">上传中…</span>
        <span v-else>+ 添加图片<br />({{ modelValue.length }}/{{ max }})</span>
      </label>
    </div>
    <p class="book-muted" style="margin-top:10px">第一张将作为封面展示，最多 {{ max }} 张，支持 JPEG、PNG、WebP，单张不超过 5 MB。</p>
  </div>
</template>
