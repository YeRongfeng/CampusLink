import { request } from './request'

export const getHealth = () => request.get<{ status: 'ok' }>('/health', { silent: true, skipAuth: true })
