export interface WorkerNodeRecord {
  id: string
  worker_id: string
  hostname: string
  concurrency: number
  active_tasks_count: number
  active_tasks: string[]
  total_completed: number
  total_failed: number
  status: 'HEALTHY' | 'BUSY' | 'OFFLINE'
  cpu_percent: number
  memory_mb: number
  last_heartbeat: string
  created_at: string
}

export interface QueueMetrics {
  total_tasks: number
  pending_tasks: number
  running_tasks: number
  completed_tasks: number
  failed_tasks: number
  retrying_tasks: number
  queue_depth: number
}

export interface QueuedTaskRecord {
  task_id: string
  job_id?: string | null
  task_type: string
  priority: 'LOW' | 'DEFAULT' | 'HIGH' | 'CRITICAL'
  payload: Record<string, any>
  created_at: string
  max_retries: number
  retry_count: number
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'RETRYING'
  assigned_worker_id?: string | null
  started_at?: string | null
  completed_at?: string | null
  result?: Record<string, any> | null
  error?: string | null
}

export interface StorageObjectRecord {
  id: string
  bucket: string
  object_key: string
  content_type: string
  size_bytes: number
  size_mb: number
  etag: string
  md5_hash: string
  sha256_hash: string
  metadata: Record<string, any>
  workspace_id?: string | null
  uploader_id?: string | null
  created_at: string
}

export interface StorageUsageSummary {
  database_catalog_summary: {
    workspace_id?: string | null
    total_objects: number
    total_bytes: number
    total_mb: number
    total_gb: number
  }
  local_storage_metrics: {
    bucket: string
    total_objects: number
    total_size_bytes: number
    total_size_mb: number
  }
}
