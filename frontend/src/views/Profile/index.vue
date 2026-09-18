<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { NAlert, NButton, NCard, NForm, NFormItem, NInput } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useAuthStore } from '../../stores/auth'
import { uploadImage } from '../../api/file'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import UserAvatar from '../../components/common/UserAvatar.vue'

const auth = useAuthStore()
const fileInput = ref<HTMLInputElement | null>(null)
const model = reactive({ nickname: '' })
watch(() => auth.currentUser?.nickname, (nickname) => { model.nickname = nickname || '' }, { immediate: true })
const form = ref<FormInst | null>(null)
const busy = ref(false)
const error = ref('')
const saved = ref(false)
const rules: FormRules = {
  nickname: [{ required: true, validator: () => model.nickname.trim().length >= 1 && model.nickname.trim().length <= 32, message: '昵称需为 1–32 个字符', trigger: ['blur', 'input'] }],
}
async function save() {
  if (busy.value) return
  try { await form.value?.validate() } catch { return }
  busy.value = true
  error.value = ''
  saved.value = false
  try { await auth.updateProfile({ nickname: model.nickname.trim() }); saved.value = true }
  catch (cause) { error.value = cause instanceof Error ? cause.message : '保存失败，请重试' }
  finally { busy.value = false }
}
async function changeAvatar(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || busy.value) return
  error.value = ''
  saved.value = false
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
    error.value = '请选择不超过 5 MB 的 JPEG、PNG 或 WebP 图片'
    return
  }
  busy.value = true
  try {
    const { url } = await uploadImage(file)
    await auth.updateProfile({ avatar: url })
    saved.value = true
  } catch (cause) { error.value = cause instanceof Error ? cause.message : '头像上传失败，请重试' }
  finally { busy.value = false }
}
</script>

<template>
  <AppContainer><main class="profile-page">
    <PageHeader title="我的 CampusLink" description="管理个人资料与校园生活" />
    <NCard v-if="auth.currentUser" class="profile-card">
      <div class="profile-identity flex items-center gap-4">
        <UserAvatar :user="auth.currentUser" :size="72" />
        <div><strong>{{ auth.currentUser.nickname }}</strong><p class="m-0 mt-1 text-[#617268]">{{ auth.currentUser.username }}</p></div>
      </div>
      <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" aria-label="选择头像" @change="changeAvatar" />
      <NButton :disabled="busy" class="mb-3" @click="fileInput?.click()">更换头像</NButton>
      <p class="mb-6 mt-0 text-sm text-[var(--text-secondary)]">支持 JPEG、PNG、WebP，最大 5 MB。</p>
      <NAlert v-if="error" type="error" class="mb-5" aria-live="polite">{{ error }}</NAlert>
      <NAlert v-if="saved" type="success" class="mb-5" aria-live="polite">资料已保存。</NAlert>
      <NForm ref="form" :model="model" :rules="rules" :disabled="busy" @submit.prevent="save">
        <NFormItem label="昵称" path="nickname" label-for="profile-nickname">
          <NInput v-model:value="model.nickname" :input-props="{ id: 'profile-nickname', autocomplete: 'nickname' }" @update:value="saved = false" />
        </NFormItem>
        <NButton attr-type="submit" type="primary" :loading="busy">保存资料</NButton>
      </NForm>
      <p class="mb-0 mt-6 text-sm text-[#617268]">用户名注册后不可修改。</p>
    </NCard>
    <NCard title="我的内容" class="mt-6">
      <div class="my-content-links"><RouterLink to="/ride/mine">我的拼车</RouterLink><RouterLink to="/quest/mine">我的悬赏</RouterLink><RouterLink to="/book/mine">我的书籍</RouterLink></div>
    </NCard>
  </main></AppContainer>
</template>
