import { request } from './request'
import type { Credentials, Registration, LoginResult, User } from '../types/user'

export const register = (data: Registration) => request.post<User>('/auth/register', data, { skipAuth: true, silent: true })
export const login = (data: Credentials) => request.post<LoginResult>('/auth/login', data, { skipAuth: true, silent: true })
