<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NForm, NFormItem, NInput } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { register } from '../../api/auth'
import { safeRedirect } from '../../router/redirect'

const router = useRouter()
const route = useRoute()
const form = ref<FormInst | null>(null)
const model = reactive({ username: '', nickname: '', password: '', confirm: '' })
const busy = ref(false)
const error = ref('')
const rules: FormRules = {
  username: [{ required: true, pattern: /^[A-Za-z0-9_]{3,32}$/, message: '使用 3–32 位字母、数字或下划线', trigger: ['blur', 'input'] }],
  nickname: [{ validator: () => model.nickname.trim().length <= 32, message: '昵称最多 32 个字符', trigger: 'blur' }],
  password: [{ required: true, min: 8, max: 128, message: '密码长度应为 8–128 个字符', trigger: ['blur', 'input'] }],
  confirm: [{ required: true, validator: () => Boolean(model.confirm) && model.confirm === model.password, message: '两次输入的密码不一致', trigger: ['blur', 'input'] }],
}
async function submit() {
  if (busy.value) return
  try { await form.value?.validate() } catch { return }
  busy.value = true
  error.value = ''
  try {
    const user = await register({ username: model.username, password: model.password, ...(model.nickname.trim() ? { nickname: model.nickname.trim() } : {}) })
    await router.replace({ path: '/login', query: { username: user.username, registered: '1', redirect: safeRedirect(route.query.redirect) } })
  } catch (cause) { error.value = cause instanceof Error ? cause.message : '注册失败，请重试' }
  finally { busy.value = false }
}
</script>

<template>
  <main class="auth-page">
    <p class="eyebrow">YOUR CAMPUS, CONNECTED</p>
    <h1 class="auth-title">加入 CampusLink</h1>
    <p class="mb-6 text-[#617268]">用一个账号，连接你的校园生活。</p>
    <NCard class="auth-card" :bordered="false">
      <NAlert v-if="error" type="error" class="mb-5" aria-live="polite">{{ error }}</NAlert>
      <NForm ref="form" :model="model" :rules="rules" :disabled="busy" @submit.prevent="submit">
        <NFormItem label="用户名" path="username" label-for="register-username">
          <NInput v-model:value="model.username" :input-props="{ id: 'register-username', autocomplete: 'username' }" placeholder="字母、数字或下划线" />
        </NFormItem>
        <NFormItem label="昵称（选填）" path="nickname" label-for="register-nickname">
          <NInput v-model:value="model.nickname" :input-props="{ id: 'register-nickname', autocomplete: 'nickname' }" placeholder="不填则使用用户名" />
        </NFormItem>
        <NFormItem label="密码" path="password" label-for="register-password">
          <NInput v-model:value="model.password" type="password" show-password-on="click" :input-props="{ id: 'register-password', autocomplete: 'new-password' }" placeholder="8–128 个字符" />
        </NFormItem>
        <NFormItem label="确认密码" path="confirm" label-for="register-confirm">
          <NInput v-model:value="model.confirm" type="password" :input-props="{ id: 'register-confirm', autocomplete: 'new-password' }" placeholder="再次输入密码" />
        </NFormItem>
        <NButton attr-type="submit" block type="primary" :loading="busy">注册</NButton>
      </NForm>
      <p class="auth-switch">已有账号？<RouterLink :to="{ path: '/login', query: { redirect: safeRedirect(route.query.redirect) } }">去登录</RouterLink></p>
    </NCard>
  </main>
</template>
