import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import * as authApi from '../api/auth'
import * as userApi from '../api/user'
import { ApiError } from '../api/request'
import type { Credentials, User, UserUpdate } from '../types/user'

export const TOKEN_KEY = 'campuslink.token'
function readToken(): string | null {
  try { return localStorage.getItem(TOKEN_KEY) } catch { return null }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(readToken())
  const currentUser = ref<User | null>(null)
  const isAuthenticated = computed(() => Boolean(token.value && currentUser.value))
  let pending: Promise<boolean> | null = null
  let revision = 0

  function logout() {
    revision++
    token.value = null
    currentUser.value = null
    pending = null
    try { localStorage.removeItem(TOKEN_KEY) } catch { /* in-memory state is still cleared */ }
  }

  async function restore(): Promise<boolean> {
    if (!token.value) return false
    if (currentUser.value) return true
    if (pending) return pending
    const version = revision
    const attempt = (async () => {
      try {
        const user = await userApi.getCurrentUser()
        if (version !== revision || !token.value) return false
        currentUser.value = user
        return true
      } catch (error) {
        if (version !== revision) return false
        if (error instanceof ApiError && error.status === 401) { logout(); return false }
        throw error
      }
    })()
    pending = attempt
    try { return await attempt } finally { if (pending === attempt) pending = null }
  }

  async function login(credentials: Credentials) {
    const version = ++revision
    const result = await authApi.login(credentials)
    if (version !== revision) return false
    try { localStorage.setItem(TOKEN_KEY, result.access_token) } catch {
      throw new Error('浏览器无法保存登录状态，请允许本站使用本地存储')
    }
    token.value = result.access_token
    currentUser.value = null
    pending = null
    return restore()
  }

  async function updateProfile(data: UserUpdate) {
    const version = revision
    const user = await userApi.updateCurrentUser(data)
    if (version === revision && token.value) currentUser.value = user
  }

  return { token, currentUser, isAuthenticated, login, logout, restore, updateProfile }
})
