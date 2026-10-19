export interface Person { id: number; nickname: string; avatar: string | null }
export interface Contact { contact_type: 'wechat' | 'qq' | 'phone'; contact_value: string }
export type Category = 'textbook' | 'reference' | 'exam' | 'literature' | 'other'
export type Condition = 'new' | 'like_new' | 'good' | 'worn'
export type TradeMethod = 'meetup' | 'delivery' | 'either'
export type BookStatus = 'listed' | 'reserved' | 'sold' | 'removed'

export interface Book {
  id: number; seller: Person; title: string; author: string; category: Category; condition_grade: Condition
  cover_image: string; price: string; original_price: string | null; discount_percent: number | null
  is_negotiable: boolean; status: BookStatus; trade_method: TradeMethod
  favorite_count: number; view_count: number; created_at: string
  favorited_at?: string | null
}
export interface BookDetail extends Book {
  isbn: string | null; description: string; cover_images: string[]; trade_location: string; updated_at: string
}
export interface BookWrite extends Contact {
  title: string; author: string; isbn: string | null; category: Category; condition_grade: Condition
  description: string; cover_images: string[]; original_price: string | null; price: string
  is_negotiable: boolean; trade_method: TradeMethod; trade_location: string
}
export interface BookRelation {
  listing_id: number; is_owner: boolean; is_favorited: boolean
  can_edit: boolean; can_reserve: boolean; can_unreserve: boolean; can_mark_sold: boolean; can_remove: boolean; can_contact: boolean
}
export interface SellerContact extends Person, Contact {}
export interface FavoriteResult { listing_id: number; is_favorited: boolean; favorite_count: number }
export interface Page<T> { items: T[]; total: number; page: number; page_size: number }

export const categoryNames: Record<Category, string> = {
  textbook: '教材', reference: '教辅', exam: '考试资料', literature: '文学读物', other: '其他',
}
export const categoryOptions = Object.entries(categoryNames).map(([value, label]) => ({ value, label }))
export const conditionNames: Record<Condition, string> = {
  new: '全新', like_new: '几乎全新', good: '轻微使用痕迹', worn: '明显使用痕迹',
}
export const conditionOptions = Object.entries(conditionNames).map(([value, label]) => ({ value, label }))
export const tradeMethodNames: Record<TradeMethod, string> = {
  meetup: '当面交易', delivery: '校内代送', either: '均可协商',
}
export const tradeMethodOptions = Object.entries(tradeMethodNames).map(([value, label]) => ({ value, label }))
export const statusNames: Record<BookStatus, string> = {
  listed: '在售', reserved: '已预定', sold: '已售出', removed: '已下架',
}
export const contactNames = { wechat: '微信', qq: 'QQ', phone: '电话' }
export const contactOptions = Object.entries(contactNames).map(([value, label]) => ({ value, label }))
export const formatTime = (value: string) => new Intl.DateTimeFormat('zh-CN', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false,
}).format(new Date(value))
