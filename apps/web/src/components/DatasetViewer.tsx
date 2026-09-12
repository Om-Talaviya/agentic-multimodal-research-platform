import React, { useState } from 'react'
import { DatasetProfile, ColumnProfile } from '../types/research'
import { Table, Database, BarChart2, Hash, Type, Calendar, HelpCircle, ChevronRight, Search, TrendingUp } from 'lucide-react'

interface DatasetViewerProps {
  dataset: DatasetProfile
  title?: string
}

export const DatasetViewer: React.FC<DatasetViewerProps> = ({
  dataset,
  title = "Dataset & Tabular Intelligence"
}) => {
  const [selectedColumn, setSelectedColumn] = useState<string | null>(
    dataset.columns && dataset.columns.length > 0 ? dataset.columns[0].name : null
  )
  const [searchFilter, setSearchFilter] = useState<string>("")
  const [previewTab, setPreviewTab] = useState<'profile' | 'data'>('profile')

  const getTypeIcon = (dataType: string) => {
    switch (dataType.toLowerCase()) {
      case 'integer':
      case 'float':
        return <Hash size={13} style={{ color: '#38bdf8' }} />
      case 'datetime':
      case 'date':
        return <Calendar size={13} style={{ color: '#34d399' }} />
      case 'string':
        return <Type size={13} style={{ color: '#c084fc' }} />
      default:
        return <HelpCircle size={13} style={{ color: '#94a3b8' }} />
    }
  }

  const numericCols = dataset.columns.filter(c => c.data_type === 'integer' || c.data_type === 'float')
  const filteredColumns = dataset.columns.filter(c => 
    c.name.toLowerCase().includes(searchFilter.toLowerCase())
  )

  const activeColProfile = dataset.columns.find(c => c.name === selectedColumn)

  return (
    <div className="card" style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', marginBottom: '24px' }}>
      {/* Header & KPI Summary Cards */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={18} style={{ color: 'var(--color-primary)' }} />
            <span>{title}</span>
            <span className="badge badge-primary">{dataset.metadata?.filename || 'Dataset'}</span>
          </h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>
            Deterministic statistical profiling and column distribution overview.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            onClick={() => setPreviewTab('profile')}
            className={`btn btn-sm ${previewTab === 'profile' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '5px 12px' }}
          >
            <BarChart2 size={13} style={{ marginRight: '5px' }} /> Column Profiler
          </button>
          <button
            onClick={() => setPreviewTab('data')}
            className={`btn btn-sm ${previewTab === 'data' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '5px 12px' }}
          >
            <Table size={13} style={{ marginRight: '5px' }} /> Data Preview
          </button>
        </div>
      </div>

      {/* KPI Metrics Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', marginBottom: '20px' }}>
        <div style={{ background: 'rgba(56, 189, 248, 0.08)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Rows</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#38bdf8', marginTop: '2px' }}>{dataset.total_rows.toLocaleString()}</div>
        </div>

        <div style={{ background: 'rgba(168, 85, 247, 0.08)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(168, 85, 247, 0.2)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Columns</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#c084fc', marginTop: '2px' }}>{dataset.total_cols}</div>
        </div>

        <div style={{ background: 'rgba(52, 211, 153, 0.08)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(52, 211, 153, 0.2)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Numeric Features</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#34d399', marginTop: '2px' }}>{numericCols.length}</div>
        </div>

        <div style={{ background: 'rgba(251, 191, 36, 0.08)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(251, 191, 36, 0.2)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Categorical / Text</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#fbbf24', marginTop: '2px' }}>{dataset.total_cols - numericCols.length}</div>
        </div>
      </div>

      {previewTab === 'profile' ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(240px, 1fr) 2fr', gap: '16px', alignItems: 'start' }}>
          {/* Column Selector List */}
          <div style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
            <div style={{ position: 'relative', marginBottom: '10px' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '9px', color: 'var(--color-text-muted)' }} />
              <input
                type="text"
                placeholder="Search columns..."
                value={searchFilter}
                onChange={e => setSearchFilter(e.target.value)}
                style={{
                  width: '100%',
                  padding: '6px 10px 6px 30px',
                  background: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.8rem',
                  color: 'var(--color-text)',
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '320px', overflowY: 'auto' }}>
              {filteredColumns.map(col => (
                <button
                  key={col.name}
                  onClick={() => setSelectedColumn(col.name)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 10px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid',
                    borderColor: selectedColumn === col.name ? 'var(--color-primary)' : 'transparent',
                    background: selectedColumn === col.name ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                    color: selectedColumn === col.name ? 'var(--color-text-bright)' : 'var(--color-text)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '0.82rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', overflow: 'hidden' }}>
                    {getTypeIcon(col.data_type)}
                    <span style={{ fontWeight: selectedColumn === col.name ? 600 : 400, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                      {col.name}
                    </span>
                  </div>
                  <ChevronRight size={13} style={{ opacity: selectedColumn === col.name ? 1 : 0.4 }} />
                </button>
              ))}
            </div>
          </div>

          {/* Active Column Deep Dive */}
          {activeColProfile ? (
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '1px solid var(--color-border)', paddingBottom: '10px' }}>
                <div>
                  <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                    {getTypeIcon(activeColProfile.data_type)}
                    <code>{activeColProfile.name}</code>
                  </h4>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Type: {activeColProfile.data_type}</span>
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <span className="badge badge-info">{activeColProfile.unique_count} Unique</span>
                  <span className="badge badge-secondary">{activeColProfile.null_count} Nulls</span>
                </div>
              </div>

              {/* Statistics for Numeric Columns */}
              {activeColProfile.mean_value !== undefined && activeColProfile.mean_value !== null ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginBottom: '16px' }}>
                  <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>Mean (Average)</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#38bdf8' }}>{activeColProfile.mean_value.toFixed(4)}</div>
                  </div>
                  <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>Median (50th %ile)</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#34d399' }}>{activeColProfile.median_value?.toFixed(4) ?? '-'}</div>
                  </div>
                  <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>Std Deviation (σ)</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#c084fc' }}>{activeColProfile.std_dev?.toFixed(4) ?? '-'}</div>
                  </div>
                  <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>Min / Max Range</div>
                    <div style={{ fontSize: '1.0rem', fontWeight: 600, color: '#fbbf24' }}>
                      [{activeColProfile.min_value} .. {activeColProfile.max_value}]
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ marginBottom: '16px', padding: '10px', background: 'rgba(0, 0, 0, 0.25)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>Value Range:</div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--color-text)' }}>
                    {activeColProfile.min_value !== undefined ? `[${activeColProfile.min_value} .. ${activeColProfile.max_value}]` : 'Categorical values'}
                  </div>
                </div>
              )}

              {/* Sample Distinct Values */}
              {activeColProfile.sample_values && activeColProfile.sample_values.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '6px' }}>Sample Observed Values:</div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {activeColProfile.sample_values.map((v, i) => (
                      <span key={i} style={{ fontSize: '0.75rem', padding: '3px 8px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                        {String(v)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '32px' }}>
              <p>Select a column to inspect its statistical profile.</p>
            </div>
          )}
        </div>
      ) : (
        /* Data Preview Grid */
        <div style={{ overflowX: 'auto', maxHeight: '360px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(0, 0, 0, 0.4)', borderBottom: '1px solid var(--color-border)' }}>
                {dataset.columns.map(col => (
                  <th key={col.name} style={{ padding: '8px 12px', fontWeight: 600, whiteSpace: 'nowrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {getTypeIcon(col.data_type)}
                      <span>{col.name}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataset.sample_rows && dataset.sample_rows.length > 0 ? (
                dataset.sample_rows.map((row, rIdx) => (
                  <tr key={rIdx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', background: rIdx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.01)' }}>
                    {dataset.columns.map(col => (
                      <td key={col.name} style={{ padding: '8px 12px', whiteSpace: 'nowrap', color: row[col.name] !== null ? 'var(--color-text)' : 'var(--color-text-muted)' }}>
                        {row[col.name] !== null && row[col.name] !== undefined ? String(row[col.name]) : <em>null</em>}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={dataset.columns.length} style={{ padding: '24px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                    No preview rows available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
