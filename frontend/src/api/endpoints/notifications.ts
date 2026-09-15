import { get, post } from '../client'

export interface Notification {
  id: number
  notification_type: string
  title: string
  body: string
  link: string
  is_read: boolean
  read_at: string | null
  created_at: string
}

export interface UnreadCount {
  unread_count: number
}

export function listNotifications(params?: {
  unread?: string
  limit?: string
}): Promise<Notification[]> {
  return get<Notification[]>('/notifications', { params })
}

export function getUnreadCount(): Promise<UnreadCount> {
  return get<UnreadCount>('/notifications/unread-count')
}

export function markAsRead(id: number): Promise<{ detail: string }> {
  return post<{ detail: string }>(`/notifications/${id}/read`)
}

export function markAllAsRead(): Promise<{ detail: string }> {
  return post<{ detail: string }>('/notifications/read-all')
}
