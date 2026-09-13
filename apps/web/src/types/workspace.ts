export interface Workspace {
  id: string
  name: string
  slug: string
  description?: string | null
  owner_id: string
  is_personal: boolean
  settings?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface WorkspaceMember {
  id: string
  workspace_id: string
  user_id: string
  role: 'owner' | 'admin' | 'researcher' | 'member' | 'viewer'
  created_at: string
}

export interface Project {
  id: string
  workspace_id: string
  name: string
  slug: string
  description?: string | null
  created_by?: string | null
  status: 'active' | 'archived'
  settings?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ProjectMetrics {
  total_jobs: number
  total_documents: number
  total_memories: number
  total_graph_entities: number
}

export interface ProjectOverview {
  project: Project
  metrics: ProjectMetrics
}
