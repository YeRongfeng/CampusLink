import { request } from '../../api/request'
import type { Book, BookDetail, BookRelation, BookWrite, FavoriteResult, Page, SellerContact } from './types'
const quiet = { silent: true }
export const booksApi = {
  list: (params: Record<string, unknown>, mine = false) => request.get<Page<Book>>(mine ? '/books/mine' : '/books', { ...quiet, params }),
  detail: (id: number) => request.get<BookDetail>(`/books/${id}`, quiet),
  relation: (id: number) => request.get<BookRelation>(`/books/${id}/relation`, quiet),
  contact: (id: number) => request.get<SellerContact>(`/books/${id}/contact`, quiet),
  save: (data: BookWrite, id?: number) => id ? request.put<BookDetail>(`/books/${id}`, data, quiet) : request.post<BookDetail>('/books', data, quiet),
  favorite: (id: number, on: boolean) => on ? request.post<FavoriteResult>(`/books/${id}/favorite`, {}, quiet) : request.delete<FavoriteResult>(`/books/${id}/favorite`, quiet),
  act: (id: number, action: 'reserve' | 'unreserve' | 'sold' | 'remove') => request.post<BookDetail>(`/books/${id}/${action}`, {}, quiet),
}
