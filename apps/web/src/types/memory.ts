export type MemoryType = 'finding' | 'insight' | 'methodology' | 'concept' | 'summary' | 'hypothesis'

export interface MemoryItem {
  id: string
  user_id?: string | null
  job_id?: string | null
  memory_type: MemoryType
  title: string
  content: string
  tags: string[]
  confidence: number
  source_type: string
  created_at?: string | null
  last_accessed_at?: string | null
  access_count: number
  metadata?: Record<string, any>
}

export interface MemoryRecallResult {
  query: string
  memories: MemoryItem[]
  total_recalled: number
}

export interface CreateMemoryPayload {
  title: string
  content: string
  memory_type?: MemoryType
  job_id?: string
  tags?: string[]
  confidence?: number
  metadata?: Record<string, any>
}

export interface UpdateMemoryPayload {
  title?: string
  content?: string
  memory_type?: MemoryType
  tags?: string[]
  confidence?: number
  metadata?: Record<string, any>
}
