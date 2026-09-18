<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import AppContainer from './AppContainer.vue'
import UserAvatar from '../common/UserAvatar.vue'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const expanded = ref(false)
const links = [{ to: '/', label: '首页' }, { to: '/ride', label: '校园拼车' }, { to: '/quest', label: '校园悬赏' }, { to: '/book', label: '二手书' }]
watch(() => route.fullPath, () => { expanded.value = false })
function logout() {
  auth.logout()
  if (route.meta.requiresAuth) void router.replace('/')
}
</script>

<template>
  <header class="app-header">
    <AppContainer>
      <div class="flex flex-wrap items-center justify-between gap-4">
        <RouterLink to="/" class="brand-link">Campus<span>Link</span><small>校园生活连接站</small></RouterLink>
        <div class="md:hidden"><NButton :aria-expanded="expanded" aria-controls="main-navigation" @click="expanded = !expanded">菜单</NButton></div>
        <nav id="main-navigation" aria-label="主导航" :class="[expanded ? 'flex' : 'hidden', 'main-nav w-full flex-col gap-4 md:flex md:w-auto md:flex-row md:items-center']">
          <RouterLink v-for="link in links" :key="link.to" :to="link.to"
            :aria-current="route.path === link.to ? 'page' : undefined"
            :class="['nav-link', (link.to === '/' ? route.path === '/' : route.path.startsWith(link.to)) ? 'is-active' : '']">{{ link.label }}</RouterLink>
          <template v-if="auth.isAuthenticated">
            <RouterLink to="/profile" class="profile-link flex items-center gap-2 no-underline">
              <UserAvatar :user="auth.currentUser" :size="28" />
              <span class="max-w-32 truncate">{{ auth.currentUser?.nickname }}</span>
            </RouterLink>
            <NButton size="small" @click="logout">退出登录</NButton>
          </template>
          <template v-else><RouterLink to="/login" class="nav-link">登录</RouterLink><RouterLink to="/register" class="signup-link">加入我们</RouterLink></template>
        </nav>
      </div>
    </AppContainer>
  </header>
</template>
