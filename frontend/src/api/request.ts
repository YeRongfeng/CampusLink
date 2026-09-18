import axios from 'axios'
import type { AxiosRequestConfig } from 'axios'
import type { ApiResponse } from '../types/api'

declare module 'axios' {
  interface AxiosRequestConfig { skipAuth?: boolean; silent?: boolean }
}

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message) }
}

let getToken: () => string | null = () => null
let onUnauthorized: (token: string) => void = () => {}
let notify: (message: string) => void = () => {}

export function configureAuthRequest(hooks: {
  getToken: () => string | null
  onUnauthorized: (token: string) => void
}) {
  getToken = hooks.getToken
  onUnauthorized = hooks.onUnauthorized
}
export function setErrorNotifier(callback: (message: string) => void) { notify = callback }

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', timeout: 10_000,
})
http.interceptors.request.use((config) => {
  const token = getToken()
  if (!config.skipAuth && token) config.headers.set('Authorization', `Bearer ${token}`)
  return config
})

let lastMessage = ''
let lastTime = 0

async function send<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const result = await http.request<ApiResponse<T>>(config)
    if (result.data?.code !== result.status || !('data' in result.data)) {
      throw new ApiError('服务返回了无法识别的响应', result.status)
    }
    return result.data.data
  } catch (cause) {
    let error: ApiError
    if (axios.isAxiosError(cause)) {
      const status = cause.response?.status || 0
      const message = cause.response?.data?.message
      error = new ApiError(
        typeof message === 'string' ? message : cause.code === 'ECONNABORTED'
          ? '请求超时，请稍后重试' : status ? '服务暂时不可用，请稍后重试' : '网络连接失败，请稍后重试', status,
      )
      const authorization = cause.config?.headers.get('Authorization')
      if (status === 401 && !config.skipAuth && typeof authorization === 'string') {
        onUnauthorized(authorization.replace(/^Bearer /, ''))
      }
    } else {
      error = cause instanceof ApiError ? cause : new ApiError('请求失败，请重试', 0)
    }
    if (!config.silent && (error.message !== lastMessage || Date.now() - lastTime > 1500)) {
      lastMessage = error.message
      lastTime = Date.now()
      notify(error.message)
    }
    throw error
  }
}

export const request = {
  get: <T>(url: string, config?: AxiosRequestConfig) => send<T>({ ...config, method: 'GET', url }),
  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) => send<T>({ ...config, method: 'POST', url, data }),
  put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) => send<T>({ ...config, method: 'PUT', url, data }),
  delete: <T>(url: string, config?: AxiosRequestConfig) => send<T>({ ...config, method: 'DELETE', url }),
}
