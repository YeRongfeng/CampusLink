import { request } from '../../api/request'
import type { Contact, Contacts, Membership, Page, Ride, RideDetail, RideWrite } from './types'
const quiet = { silent: true }
export const ridesApi = {
  list: (params: Record<string, unknown>, mine = false) => request.get<Page<Ride>>(mine ? '/rides/mine' : '/rides', { ...quiet, params }),
  detail: (id: number) => request.get<RideDetail>(`/rides/${id}`, quiet),
  membership: (id: number) => request.get<Membership>(`/rides/${id}/membership`, quiet),
  contacts: (id: number) => request.get<Contacts>(`/rides/${id}/contacts`, quiet),
  save: (data: RideWrite, id?: number) => id ? request.put<RideDetail>(`/rides/${id}`, data, quiet) : request.post<RideDetail>('/rides', data, quiet),
  join: (id: number, data: Contact) => request.post<Membership>(`/rides/${id}/join`, data, quiet),
  act: (id: number, action: 'leave' | 'cancel' | 'complete') => request.post(`/rides/${id}/${action}`, {}, quiet),
}
