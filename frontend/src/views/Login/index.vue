<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NForm, NFormItem, NInput } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useAuthStore } from '../../stores/auth'
import { safeRedirect } from '../../router/redirect'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const form = ref<FormInst | null>(null)
const model = reactive({ username: typeof route.query.username === 'string' ? route.query.username : '', password: '' })
const busy = ref(false)
const error = ref('')
const redirect = computed(() => safeRedirect(route.query.redirect))
const rules: FormRules = {
  username: [{ required: true, pattern: /^[A-Za-z0-9_]{3,32}$/, message: '请输入 3–32 位字母、数字或下划线', trigger: ['blur', 'input'] }],
  password: [{ required: true, min: 8, max: 128, message: '密码长度应为 8–128 个字符', trigger: ['blur', 'input'] }],
}
async function submit() {
  if (busy.value) return
  try { await form.value?.validate() } catch { return }
  busy.value = true
  error.value = ''
  try {
    if (await auth.login(model)) await router.replace(redirect.value)
    else error.value = '登录状态已变化，请重试'
  } catch (cause) { error.value = cause instanceof Error ? cause.message : '登录失败，请重试' }
  finally { busy.value = false }
}
async function retrySession() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    if (await auth.restore()) await router.replace(redirect.value)
    else error.value = '登录已失效，请重新登录'
  } catch (cause) { error.value = cause instanceof Error ? cause.message : '连接失败，请重试' }
  finally { busy.value = false }
}
</script>

<template>
  <main class="auth-page">
    <p class="eyebrow">YOUR CAMPUS, CONNECTED</p>
    <h1 class="auth-title">欢迎回来</h1>
    <p class="mb-6 text-[#617268]">登录后管理你的校园生活。</p>
    <NCard class="auth-card" :bordered="false">
      <NAlert v-if="route.query.registered === '1'" type="success" class="mb-5">注册成功，请使用刚才的密码登录。</NAlert>
      <NAlert v-if="route.query.reason === 'expired'" type="warning" class="mb-5">登录已过期，请重新登录。</NAlert>
      <NAlert v-if="route.query.reason === 'connection'" type="warning" class="mb-5">
        暂时无法验证登录状态，请检查连接后重试。
        <NButton v-if="auth.token" class="mt-3" :loading="busy" @click="retrySession">重新验证登录</NButton>
      </NAlert>
      <NAlert v-if="error" type="error" class="mb-5" aria-live="polite">{{ error }}</NAlert>
      <NForm ref="form" :model="model" :rules="rules" :disabled="busy" @submit.prevent="submit">
        <NFormItem label="用户名" path="username" label-for="login-username">
          <NInput v-model:value="model.username" :input-props="{ id: 'login-username', autocomplete: 'username' }" placeholder="请输入用户名" />
        </NFormItem>
        <NFormItem label="密码" path="password" label-for="login-password">
          <NInput v-model:value="model.password" type="password" show-password-on="click" :input-props="{ id: 'login-password', autocomplete: 'current-password' }" placeholder="请输入密码" />
        </NFormItem>
        <NButton attr-type="submit" block type="primary" :loading="busy">登录</NButton>
      </NForm>
      <p class="auth-switch">还没有账号？<RouterLink :to="{ path: '/register', query: { redirect } }">立即注册</RouterLink></p>
    </NCard>
  </main>
</template>
