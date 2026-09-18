import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { AxiosError, AxiosHeaders } from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { ApiError, configureAuthRequest, http, request, setErrorNotifier } from '../src/api/request'
import { TOKEN_KEY, useAuthStore } from '../src/stores/auth'
import { safeRedirect } from '../src/router/redirect'

const user = { id: 1, username: 'student', nickname: '同学', avatar: null, created_at: '', updated_at: '' }
const saved = new Map<string, string>()

function ok(config: InternalAxiosRequestConfig, data: unknown) {
  return { status: 200, statusText: 'OK', config, headers: new AxiosHeaders(), data: { code: 200, message: 'success', data } }
}
function fail(config: InternalAxiosRequestConfig, status: number) {
  return new AxiosError('failure', 'ERR_BAD_RESPONSE', config, null, {
    status, statusText: '', config, headers: new AxiosHeaders(), data: { code: status, message: '请求失败', data: null },
  })
}
function setup(token: string | null = 'saved-token') {
  if (token) saved.set(TOKEN_KEY, token)
  const auth = useAuthStore()
  configureAuthRequest({ getToken: () => auth.token, onUnauthorized: (sent) => { if (auth.token === sent) auth.logout() } })
  return auth
}

beforeEach(() => {
  saved.clear()
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => saved.get(key) ?? null,
    setItem: (key: string, value: string) => saved.set(key, value),
    removeItem: (key: string) => saved.delete(key),
  })
  vi.stubGlobal('window', { location: { origin: 'http://localhost:5173' } })
  setActivePinia(createPinia())
  setErrorNotifier(() => {})
})

describe('authentication state and requests', () => {
  it('restores the current user once and adds the saved bearer token', async () => {
    const auth = setup()
    const adapter = vi.fn(async (config: InternalAxiosRequestConfig) => {
      expect(config.headers.get('Authorization')).toBe('Bearer saved-token')
      return ok(config, user)
    })
    http.defaults.adapter = adapter
    await Promise.all([auth.restore(), auth.restore()])
    expect(adapter).toHaveBeenCalledTimes(1)
    expect(auth.isAuthenticated).toBe(true)
    expect(auth.currentUser).toEqual(user)
    expect(saved.has('currentUser')).toBe(false)
  })

  it('clears an expired session on 401', async () => {
    const auth = setup()
    http.defaults.adapter = async (config) => { throw fail(config, 401) }
    expect(await auth.restore()).toBe(false)
    expect(auth.token).toBeNull()
    expect(auth.currentUser).toBeNull()
    expect(saved.has(TOKEN_KEY)).toBe(false)
  })

  it('retains the token on a temporary network failure and can retry', async () => {
    const auth = setup()
    http.defaults.adapter = async (config) => { throw new AxiosError('Network Error', 'ERR_NETWORK', config) }
    await expect(auth.restore()).rejects.toMatchObject({ status: 0 })
    expect(auth.token).toBe('saved-token')
    http.defaults.adapter = async (config) => ok(config, user)
    expect(await auth.restore()).toBe(true)
  })

  it('does not resurrect a user when a pending restore finishes after logout', async () => {
    const auth = setup()
    let finish!: () => void
    let started!: () => void
    const ready = new Promise<void>((resolve) => { started = resolve })
    http.defaults.adapter = (config) => new Promise((resolve) => { finish = () => resolve(ok(config, user)); started() })
    const pending = auth.restore()
    await ready
    auth.logout()
    finish()
    expect(await pending).toBe(false)
    expect(auth.currentUser).toBeNull()
    expect(auth.isAuthenticated).toBe(false)
  })

  it('does not invalidate a newer session when an old request returns 401', async () => {
    const auth = setup()
    let failOld!: () => void
    let started!: () => void
    const ready = new Promise<void>((resolve) => { started = resolve })
    http.defaults.adapter = (config) => new Promise((_, reject) => { failOld = () => reject(fail(config, 401)); started() })
    const old = request.get('/users/me', { silent: true })
    const rejected = expect(old).rejects.toBeInstanceOf(ApiError)
    await ready
    auth.token = 'new-token'
    failOld()
    await rejected
    expect(auth.token).toBe('new-token')
  })

  it('logs in without a bearer header then loads the user with the new token', async () => {
    const auth = setup(null)
    http.defaults.adapter = async (config) => {
      if (config.url === '/auth/login') {
        expect(config.headers.has('Authorization')).toBe(false)
        return ok(config, { access_token: 'new-token', token_type: 'bearer', expires_in: 86400 })
      }
      expect(config.headers.get('Authorization')).toBe('Bearer new-token')
      return ok(config, user)
    }
    expect(await auth.login({ username: 'student', password: 'test-password' })).toBe(true)
    expect(saved.get(TOKEN_KEY)).toBe('new-token')
    expect(auth.currentUser).toEqual(user)
    auth.logout()
    expect(auth.isAuthenticated).toBe(false)
  })

  it('does not clear an existing session on a failed login request', async () => {
    const auth = setup()
    http.defaults.adapter = async (config) => { throw fail(config, 401) }
    await expect(auth.login({ username: 'student', password: 'wrong-password' })).rejects.toMatchObject({ status: 401 })
    expect(auth.token).toBe('saved-token')
  })

  it('unwraps envelopes and reports timeouts', async () => {
    setup(null)
    http.defaults.adapter = async (config) => ok(config, { items: [], total: 0, page: 1, page_size: 20 })
    await expect(request.get('/example')).resolves.toEqual({ items: [], total: 0, page: 1, page_size: 20 })
    http.defaults.adapter = async (config) => { throw new AxiosError('timeout', 'ECONNABORTED', config) }
    await expect(request.get('/example')).rejects.toMatchObject({ message: '请求超时，请稍后重试', status: 0 })
  })
})

describe('safe return routes', () => {
  it.each(['https://evil.example', '//evil.example', '/\\evil.example', '/login', '/register?redirect=/profile', undefined])('rejects %s', (path) => {
    expect(safeRedirect(path)).toBe('/')
  })
  it('preserves a local path, query and hash', () => {
    expect(safeRedirect('/profile?tab=info#name')).toBe('/profile?tab=info#name')
  })
})
