import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import {
  WorkerNodeRecord,
  QueueMetrics,
  StorageObjectRecord,
  StorageUsageSummary
} from '../types/infrastructure'
import {
  Server,
  HardDrive,
  Layers,
  RefreshCw,
  Plus,
  Link,
  Copy,
  Check,
  Box,
  Activity
} from 'lucide-react'

export function ProductionInfrastructurePage() {
  const [activeTab, setActiveTab] = useState<'topology' | 'queue' | 'storage'>('topology')
  const [workers, setWorkers] = useState<WorkerNodeRecord[]>([])
  const [queueMetrics, setQueueMetrics] = useState<QueueMetrics | null>(null)
  const [storageObjects, setStorageObjects] = useState<StorageObjectRecord[]>([])
  const [storageUsage, setStorageUsage] = useState<StorageUsageSummary | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Modals
  const [showHeartbeatModal, setShowHeartbeatModal] = useState(false)
  const [showEnqueueModal, setShowEnqueueModal] = useState(false)
  const [showPresignedModal, setShowPresignedModal] = useState(false)
  const [selectedStorageKey, setSelectedStorageKey] = useState('')
  const [generatedPresignedUrl, setGeneratedPresignedUrl] = useState<string | null>(null)
  const [copiedUrl, setCopiedUrl] = useState(false)

  // Form states
  const [hbWorkerId, setHbWorkerId] = useState('worker-node-1')
  const [hbHostname, setHbHostname] = useState('worker-us-east.cluster.local')
  const [hbConcurrency, setHbConcurrency] = useState(4)
  const [hbCpu, setHbCpu] = useState(18.5)
  const [hbMemory, setHbMemory] = useState(380.0)

  const [taskType, setTaskType] = useState('research_dag')
  const [taskPriority, setTaskPriority] = useState<'LOW' | 'DEFAULT' | 'HIGH' | 'CRITICAL'>('HIGH')
  const [taskPayloadJson, setTaskPayloadJson] = useState('{\n  "query": "Quantum Machine Learning Scaling"\n}')

  useEffect(() => {
    fetchInfrastructureData()
  }, [])

  const fetchInfrastructureData = async () => {
    setIsLoading(true)
    try {
      const [workerRes, queueRes, storageObjRes, usageRes] = await Promise.all([
        api.get('/system/workers'),
        api.get('/system/queue/status'),
        api.get('/system/storage/objects'),
        api.get('/system/storage/usage'),
      ])
      setWorkers(workerRes.data)
      setQueueMetrics(queueRes.data)
      setStorageObjects(storageObjRes.data)
      setStorageUsage(usageRes.data)
    } catch (err) {
      console.error('Failed to fetch infrastructure data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendHeartbeat = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/system/workers/heartbeat', {
        worker_id: hbWorkerId,
        hostname: hbHostname,
        concurrency: hbConcurrency,
        cpu_percent: hbCpu,
        memory_mb: hbMemory,
        status: 'HEALTHY',
      })
      setShowHeartbeatModal(false)
      fetchInfrastructureData()
    } catch (err) {
      console.error('Failed to send heartbeat:', err)
    }
  }

  const handleEnqueueTask = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      let parsedPayload = {}
      try {
        parsedPayload = JSON.parse(taskPayloadJson)
      } catch (e) {
        parsedPayload = { raw: taskPayloadJson }
      }

      await api.post('/system/queue/tasks', {
        task_type: taskType,
        priority: taskPriority,
        payload: parsedPayload,
      })
      setShowEnqueueModal(false)
      fetchInfrastructureData()
    } catch (err) {
      console.error('Failed to enqueue task:', err)
    }
  }

  const handleGeneratePresignedUrl = async (objectKey: string) => {
    setSelectedStorageKey(objectKey)
    try {
      const res = await api.post('/system/storage/presigned-url', {
        object_key: objectKey,
        operation: 'get_object',
        expires_in_seconds: 3600,
      })
      setGeneratedPresignedUrl(res.data.url)
      setShowPresignedModal(true)
    } catch (err) {
      console.error('Failed to generate presigned URL:', err)
    }
  }

  const handleCopyPresignedUrl = () => {
    if (generatedPresignedUrl) {
      navigator.clipboard.writeText(generatedPresignedUrl)
      setCopiedUrl(true)
      setTimeout(() => setCopiedUrl(false), 2000)
    }
  }

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Server style={{ width: '2rem', height: '2rem', color: 'var(--color-primary)' }} />
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0, color: 'var(--color-text-primary)' }}>
              Production Infrastructure & Worker Cluster
            </h1>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '0.2rem 0.6rem',
              borderRadius: '9999px',
              backgroundColor: 'rgba(56, 189, 248, 0.15)',
              color: 'var(--color-primary)',
              border: '1px solid rgba(56, 189, 248, 0.3)'
            }}>
              Generation 6 Standard
            </span>
          </div>
          <p style={{ color: 'var(--color-text-secondary)', margin: 0, fontSize: '0.9rem' }}>
            Distributed asynchronous task queue, worker cluster topology, and S3/MinIO compatible blob storage.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={fetchInfrastructureData}
            disabled={isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.6rem 1rem',
              borderRadius: '0.5rem',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-primary)',
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            <RefreshCw style={{ width: '1rem', height: '1rem', animation: isLoading ? 'spin 1s linear infinite' : 'none' }} />
            Refresh
          </button>

          {activeTab === 'topology' && (
            <button
              onClick={() => setShowHeartbeatModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.6rem 1rem',
                borderRadius: '0.5rem',
                backgroundColor: 'var(--color-primary)',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              <Activity style={{ width: '1rem', height: '1rem' }} />
              Register / Pulse Worker
            </button>
          )}

          {activeTab === 'queue' && (
            <button
              onClick={() => setShowEnqueueModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.6rem 1rem',
                borderRadius: '0.5rem',
                backgroundColor: 'var(--color-primary)',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              <Plus style={{ width: '1rem', height: '1rem' }} />
              Enqueue Task
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--color-border)', marginBottom: '1.5rem' }}>
        <button
          onClick={() => setActiveTab('topology')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            backgroundColor: 'transparent',
            border: 'none',
            borderBottom: activeTab === 'topology' ? '2px solid var(--color-primary)' : '2px solid transparent',
            color: activeTab === 'topology' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <Server style={{ width: '1rem', height: '1rem' }} />
          Worker Cluster ({workers.length})
        </button>

        <button
          onClick={() => setActiveTab('queue')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            backgroundColor: 'transparent',
            border: 'none',
            borderBottom: activeTab === 'queue' ? '2px solid var(--color-primary)' : '2px solid transparent',
            color: activeTab === 'queue' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <Layers style={{ width: '1rem', height: '1rem' }} />
          Distributed Queue ({queueMetrics?.queue_depth ?? 0} Depth)
        </button>

        <button
          onClick={() => setActiveTab('storage')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            backgroundColor: 'transparent',
            border: 'none',
            borderBottom: activeTab === 'storage' ? '2px solid var(--color-primary)' : '2px solid transparent',
            color: activeTab === 'storage' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <HardDrive style={{ width: '1rem', height: '1rem' }} />
          Blob Object Storage ({storageObjects.length} Blobs)
        </button>
      </div>

      {/* TOPOLOGY TAB */}
      {activeTab === 'topology' && (
        <div>
          {/* Quick Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Total Workers</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>{workers.length}</div>
            </div>
            <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Healthy Nodes</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-success)' }}>
                {workers.filter(w => w.status === 'HEALTHY' || w.status === 'BUSY').length}
              </div>
            </div>
            <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Active Tasks Running</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)' }}>
                {workers.reduce((acc, w) => acc + w.active_tasks_count, 0)}
              </div>
            </div>
            <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Total Completed Tasks</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                {workers.reduce((acc, w) => acc + w.total_completed, 0)}
              </div>
            </div>
          </div>

          {/* Workers Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '1.25rem' }}>
            {workers.map((worker) => (
              <div
                key={worker.id}
                style={{
                  padding: '1.5rem',
                  borderRadius: '0.75rem',
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Server style={{ width: '1.1rem', height: '1.1rem', color: 'var(--color-primary)' }} />
                      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: 'var(--color-text-primary)' }}>
                        {worker.worker_id}
                      </h3>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>{worker.hostname}</span>
                  </div>

                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    padding: '0.25rem 0.6rem',
                    borderRadius: '0.375rem',
                    backgroundColor: worker.status === 'HEALTHY'
                      ? 'rgba(34, 197, 94, 0.15)'
                      : worker.status === 'BUSY'
                      ? 'rgba(234, 179, 8, 0.15)'
                      : 'rgba(239, 68, 68, 0.15)',
                    color: worker.status === 'HEALTHY'
                      ? 'var(--color-success)'
                      : worker.status === 'BUSY'
                      ? '#eab308'
                      : '#ef4444',
                  }}>
                    {worker.status}
                  </span>
                </div>

                {/* Resource Bars */}
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
                    <span style={{ color: 'var(--color-text-secondary)' }}>CPU Utilization:</span>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{worker.cpu_percent}%</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', borderRadius: '3px', backgroundColor: 'var(--color-surface-hover)', overflow: 'hidden' }}>
                    <div style={{ width: `${Math.min(worker.cpu_percent, 100)}%`, height: '100%', backgroundColor: worker.cpu_percent > 80 ? '#ef4444' : 'var(--color-primary)' }} />
                  </div>
                </div>

                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Memory Usage:</span>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{worker.memory_mb} MB</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', borderRadius: '3px', backgroundColor: 'var(--color-surface-hover)', overflow: 'hidden' }}>
                    <div style={{ width: `${Math.min((worker.memory_mb / 2048) * 100, 100)}%`, height: '100%', backgroundColor: 'var(--color-primary)' }} />
                  </div>
                </div>

                {/* Task Concurrency */}
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--color-border)', fontSize: '0.8rem' }}>
                  <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Active Tasks: </span>
                    <strong style={{ color: 'var(--color-text-primary)' }}>{worker.active_tasks_count} / {worker.concurrency}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Completed: </span>
                    <strong style={{ color: 'var(--color-success)' }}>{worker.total_completed}</strong>
                  </div>
                </div>
              </div>
            ))}

            {workers.length === 0 && (
              <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', backgroundColor: 'var(--color-surface)', borderRadius: '0.75rem', border: '1px solid var(--color-border)' }}>
                <Server style={{ width: '3rem', height: '3rem', color: 'var(--color-text-secondary)', marginBottom: '1rem' }} />
                <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>No Active Worker Nodes Found</h3>
                <p style={{ color: 'var(--color-text-secondary)', marginBottom: '1rem', fontSize: '0.9rem' }}>
                  Register a worker node to start distributed DAG task processing.
                </p>
                <button
                  onClick={() => setShowHeartbeatModal(true)}
                  style={{
                    padding: '0.6rem 1.25rem',
                    borderRadius: '0.5rem',
                    backgroundColor: 'var(--color-primary)',
                    border: 'none',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Register Worker Node
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* QUEUE TAB */}
      {activeTab === 'queue' && (
        <div>
          {/* Queue Metrics */}
          {queueMetrics && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Queue Depth</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)' }}>{queueMetrics.queue_depth}</div>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Pending</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#eab308' }}>{queueMetrics.pending_tasks}</div>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Running</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)' }}>{queueMetrics.running_tasks}</div>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Completed</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-success)' }}>{queueMetrics.completed_tasks}</div>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Retrying / Failed</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#ef4444' }}>{queueMetrics.failed_tasks + queueMetrics.retrying_tasks}</div>
              </div>
            </div>
          )}

          {/* Queue Info Card */}
          <div style={{ padding: '1.5rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <Layers style={{ width: '1.2rem', height: '1.2rem', color: 'var(--color-primary)' }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: 'var(--color-text-primary)' }}>
                Distributed Priority Task Dispatcher
              </h3>
            </div>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              The platform executes research jobs using a Celery/Redis compatible priority heap dispatch engine. Tasks are dequeued by healthy cluster workers based on weighted priority: <code>CRITICAL (1) &gt; HIGH (2) &gt; DEFAULT (3) &gt; LOW (4)</code>.
            </p>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                onClick={() => setShowEnqueueModal(true)}
                style={{
                  padding: '0.6rem 1.25rem',
                  borderRadius: '0.5rem',
                  backgroundColor: 'var(--color-primary)',
                  border: 'none',
                  color: '#fff',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <Plus style={{ width: '1rem', height: '1rem' }} />
                Submit New Async Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STORAGE TAB */}
      {activeTab === 'storage' && (
        <div>
          {/* Storage Metrics */}
          {storageUsage && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Cataloged Blobs</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                  {storageUsage.database_catalog_summary.total_objects}
                </div>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Total Stored Volume</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)' }}>
                  {storageUsage.database_catalog_summary.total_mb} MB
                </div>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: '0.75rem', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>Default Bucket</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  <code>{storageUsage.local_storage_metrics.bucket}</code>
                </div>
              </div>
            </div>
          )}

          {/* Objects Table */}
          <div style={{ backgroundColor: 'var(--color-surface)', borderRadius: '0.75rem', border: '1px solid var(--color-border)', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                  <th style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>OBJECT KEY</th>
                  <th style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>BUCKET</th>
                  <th style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>CONTENT TYPE</th>
                  <th style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>SIZE</th>
                  <th style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>MD5 HASH</th>
                  <th style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {storageObjects.map((obj) => (
                  <tr key={obj.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Box style={{ width: '1rem', height: '1rem', color: 'var(--color-primary)' }} />
                        <code>{obj.object_key}</code>
                      </div>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)' }}>{obj.bucket}</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)' }}>
                      <span style={{ padding: '0.2rem 0.5rem', borderRadius: '0.25rem', backgroundColor: 'var(--color-surface-hover)', fontSize: '0.75rem' }}>
                        {obj.content_type}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-text-primary)' }}>{obj.size_mb} MB</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {obj.md5_hash ? `${obj.md5_hash.slice(0, 10)}...` : '-'}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <button
                        onClick={() => handleGeneratePresignedUrl(obj.object_key)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          padding: '0.35rem 0.65rem',
                          borderRadius: '0.375rem',
                          backgroundColor: 'var(--color-surface-hover)',
                          border: '1px solid var(--color-border)',
                          color: 'var(--color-text-primary)',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                        }}
                      >
                        <Link style={{ width: '0.85rem', height: '0.85rem' }} />
                        Presigned URL
                      </button>
                    </td>
                  </tr>
                ))}

                {storageObjects.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--color-text-secondary)' }}>
                      No storage objects cataloged in blob storage.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* HEARTBEAT MODAL */}
      {showHeartbeatModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            width: '480px',
            backgroundColor: 'var(--color-surface)',
            borderRadius: '0.75rem',
            border: '1px solid var(--color-border)',
            padding: '1.5rem',
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, margin: '0 0 1rem 0', color: 'var(--color-text-primary)' }}>
              Worker Node Heartbeat Registration
            </h3>

            <form onSubmit={handleSendHeartbeat}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                  Worker ID
                </label>
                <input
                  type="text"
                  value={hbWorkerId}
                  onChange={(e) => setHbWorkerId(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    borderRadius: '0.375rem',
                    backgroundColor: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-primary)',
                  }}
                  required
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                  Hostname
                </label>
                <input
                  type="text"
                  value={hbHostname}
                  onChange={(e) => setHbHostname(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    borderRadius: '0.375rem',
                    backgroundColor: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-primary)',
                  }}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                    Concurrency
                  </label>
                  <input
                    type="number"
                    value={hbConcurrency}
                    onChange={(e) => setHbConcurrency(Number(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      borderRadius: '0.375rem',
                      backgroundColor: 'var(--color-background)',
                      border: '1px solid var(--color-border)',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                    CPU %
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={hbCpu}
                    onChange={(e) => setHbCpu(Number(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      borderRadius: '0.375rem',
                      backgroundColor: 'var(--color-background)',
                      border: '1px solid var(--color-border)',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                    Memory MB
                  </label>
                  <input
                    type="number"
                    step="1"
                    value={hbMemory}
                    onChange={(e) => setHbMemory(Number(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      borderRadius: '0.375rem',
                      backgroundColor: 'var(--color-background)',
                      border: '1px solid var(--color-border)',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowHeartbeatModal(false)}
                  style={{
                    padding: '0.6rem 1rem',
                    borderRadius: '0.375rem',
                    backgroundColor: 'var(--color-surface-hover)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-primary)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '0.6rem 1.25rem',
                    borderRadius: '0.375rem',
                    backgroundColor: 'var(--color-primary)',
                    border: 'none',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Pulse Heartbeat
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ENQUEUE MODAL */}
      {showEnqueueModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            width: '520px',
            backgroundColor: 'var(--color-surface)',
            borderRadius: '0.75rem',
            border: '1px solid var(--color-border)',
            padding: '1.5rem',
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, margin: '0 0 1rem 0', color: 'var(--color-text-primary)' }}>
              Enqueue Background Task
            </h3>

            <form onSubmit={handleEnqueueTask}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                    Task Type
                  </label>
                  <select
                    value={taskType}
                    onChange={(e) => setTaskType(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem',
                      borderRadius: '0.375rem',
                      backgroundColor: 'var(--color-background)',
                      border: '1px solid var(--color-border)',
                      color: 'var(--color-text-primary)',
                    }}
                  >
                    <option value="research_dag">research_dag</option>
                    <option value="multimodal_ingest">multimodal_ingest</option>
                    <option value="model_eval">model_eval</option>
                    <option value="memory_consolidation">memory_consolidation</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                    Priority
                  </label>
                  <select
                    value={taskPriority}
                    onChange={(e) => setTaskPriority(e.target.value as any)}
                    style={{
                      width: '100%',
                      padding: '0.6rem',
                      borderRadius: '0.375rem',
                      backgroundColor: 'var(--color-background)',
                      border: '1px solid var(--color-border)',
                      color: 'var(--color-text-primary)',
                    }}
                  >
                    <option value="CRITICAL">CRITICAL (1)</option>
                    <option value="HIGH">HIGH (2)</option>
                    <option value="DEFAULT">DEFAULT (3)</option>
                    <option value="LOW">LOW (4)</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem', color: 'var(--color-text-secondary)' }}>
                  Payload (JSON)
                </label>
                <textarea
                  rows={5}
                  value={taskPayloadJson}
                  onChange={(e) => setTaskPayloadJson(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    borderRadius: '0.375rem',
                    backgroundColor: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-primary)',
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowEnqueueModal(false)}
                  style={{
                    padding: '0.6rem 1rem',
                    borderRadius: '0.375rem',
                    backgroundColor: 'var(--color-surface-hover)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-primary)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '0.6rem 1.25rem',
                    borderRadius: '0.375rem',
                    backgroundColor: 'var(--color-primary)',
                    border: 'none',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Enqueue
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* PRESIGNED URL MODAL */}
      {showPresignedModal && generatedPresignedUrl && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            width: '560px',
            backgroundColor: 'var(--color-surface)',
            borderRadius: '0.75rem',
            border: '1px solid var(--color-border)',
            padding: '1.5rem',
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, margin: '0 0 0.5rem 0', color: 'var(--color-text-primary)' }}>
              Presigned Blob URL Generated
            </h3>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '1rem' }}>
              Direct authenticated access URL for object <code>{selectedStorageKey}</code>. Valid for 1 hour.
            </p>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem',
              borderRadius: '0.375rem',
              backgroundColor: 'var(--color-background)',
              border: '1px solid var(--color-border)',
              marginBottom: '1.5rem',
            }}>
              <input
                type="text"
                readOnly
                value={generatedPresignedUrl}
                style={{
                  flex: 1,
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: 'var(--color-text-primary)',
                  fontSize: '0.8rem',
                  fontFamily: 'monospace',
                }}
              />
              <button
                onClick={handleCopyPresignedUrl}
                style={{
                  padding: '0.4rem 0.75rem',
                  borderRadius: '0.25rem',
                  backgroundColor: 'var(--color-primary)',
                  border: 'none',
                  color: '#fff',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                }}
              >
                {copiedUrl ? <Check style={{ width: '0.75rem', height: '0.75rem' }} /> : <Copy style={{ width: '0.75rem', height: '0.75rem' }} />}
                {copiedUrl ? 'Copied' : 'Copy'}
              </button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowPresignedModal(false)}
                style={{
                  padding: '0.6rem 1.25rem',
                  borderRadius: '0.375rem',
                  backgroundColor: 'var(--color-surface-hover)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-primary)',
                  cursor: 'pointer',
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
