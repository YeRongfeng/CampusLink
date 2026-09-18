import { request } from './request'

export function uploadImage(file: File) {
  const data = new FormData()
  data.append('file', file)
  return request.post<{ url: string }>('/files/upload', data, { silent: true, timeout: 30_000 })
}
