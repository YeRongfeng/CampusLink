import { request } from './request'
import type { User, UserUpdate } from '../types/user'

export const getCurrentUser = () => request.get<User>('/users/me', { silent: true })
export const updateCurrentUser = (data: UserUpdate) => request.put<User>('/users/me', data, { silent: true })
