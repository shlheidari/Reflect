export interface AdminParticipant {
  id: number
  username: string
  display_name: string
  avatar: string | null
  event: number
  is_active: boolean
  last_login: string | null
  ratings_given_count: number
  ratings_received_count: number
  created_at: string
  updated_at: string
}

export interface PaginatedParticipants {
  count: number
  next: string | null
  previous: string | null
  results: AdminParticipant[]
}

export interface AdminParticipantCreatePayload {
  username: string
  password?: string
  display_name: string
  event: number
  is_active?: boolean
}

export interface CreateParticipantResult extends AdminParticipant {
  generated_password?: string
}

export type AdminParticipantUpdatePayload = Partial<Pick<AdminParticipant, 'display_name' | 'is_active'>>

export interface ResetPasswordPayload {
  new_password?: string
}

export interface ResetPasswordResult {
  detail: string
  generated_password?: string
}
