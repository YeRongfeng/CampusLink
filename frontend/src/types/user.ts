export interface User {
  id: number
  username: string
  nickname: string
  avatar: string | null
  created_at: string
  updated_at: string
}
export interface Credentials { username: string; password: string }
export interface Registration extends Credentials { nickname?: string }
export interface UserUpdate { nickname?: string; avatar?: string | null }
export interface LoginResult { access_token: string; token_type: string; expires_in: number }
