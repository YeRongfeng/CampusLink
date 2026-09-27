export interface Location {
  address: string; longitude: number; latitude: number; poi_id: string | null; adcode: string | null
  source: 'poi' | 'map' | 'geolocation'; coordinate_system: 'gcj02'
}
export interface Person { id: number; nickname: string; avatar: string | null }
export interface Contact { contact_type: 'wechat' | 'qq' | 'phone'; contact_value: string }
export interface Ride {
  id: number; owner: Person; origin: string; destination: string; meeting_point: string
  departure_at: string; recruit_seats: number; joined_count: number; remaining_seats: number
  estimated_cost: string | null; status: 'scheduled' | 'cancelled' | 'completed'
  display_status: 'open' | 'full' | 'departed' | 'cancelled' | 'completed'; created_at: string
  member_status: 'joined' | 'withdrawn' | null
  origin_distance_km?: number | null; destination_distance_km?: number | null
}
export interface RideDetail extends Ride {
  origin_location: Location | null; destination_location: Location | null; meeting_location: Location | null
  meeting_note: string; note: string; updated_at: string; server_time: string
}
export interface RideWrite extends Contact {
  origin: string; destination: string; meeting_point: string
  origin_location: Location | null; destination_location: Location | null; meeting_location: Location | null
  meeting_note: string; departure_at: string; recruit_seats: number; estimated_cost: string | null; note: string
}
export interface Membership {
  trip_id: number; role: 'owner' | 'member' | 'visitor'; member_status: 'joined' | 'withdrawn' | null
  can_join: boolean; can_leave: boolean; can_edit: boolean; can_cancel: boolean; can_complete: boolean
}
export interface Contacts { owner: Person & Contact; active_members: (Person & Contact)[] }
export interface Page<T> { items: T[]; total: number; page: number; page_size: number }
export const statusNames = { open: '可报名', full: '已满员', departed: '已到出发时间', cancelled: '已取消', completed: '已完成' }
export const contactNames = { wechat: '微信', qq: 'QQ', phone: '电话' }
export const contactOptions = Object.entries(contactNames).map(([value, label]) => ({ value, label }))
export const formatTime = (value: string) => new Intl.DateTimeFormat('zh-CN', {
  timeZone: 'Asia/Shanghai', month: 'long', day: 'numeric', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
}).format(new Date(value))
export const toBeijingInput = (value: string) => new Date(Date.parse(value) + 8 * 3600000).toISOString().slice(0, 16)
