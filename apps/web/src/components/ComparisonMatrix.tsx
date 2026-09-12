import React, { useState } from 'react'
import { MethodologyComparisonMatrix } from '../types/research'
import { GitCompare, CheckCircle2, AlertCircle, Sparkles, Copy, Check } from 'lucide-react'

interface ComparisonMatrixProps {
  matrix: MethodologyComparisonMatrix
}

export const ComparisonMatrix: React.FC<ComparisonMatrixProps> = ({ matrix }) => {
  const [filterFocus, setFilterFocus] = useState<string>('all')
  const [copied, setCopied] = useState<boolean>(false)

  const handleCopy = () => {
    if (matrix.comparison_matrix_markdown) {
      navigator.clipboard.writeText(matrix.comparison_matrix_markdown)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div
      style={{
        backgroundColor: 'var(--bg-card)',
        borderRadius: '12px',
        border: '1px solid var(--border-subtle)',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitCompare size={20} style={{ color: 'var(--accent-purple)' }} />
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Cross-Paper Methodology Comparison
            </h3>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              Synthesizing {matrix.paper_count} research preprints and manuscripts
            </span>
          </div>
        </div>

        <button
          onClick={handleCopy}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)',
            backgroundColor: 'rgba(30, 41, 59, 0.6)',
            color: copied ? 'var(--accent-emerald)' : '#cbd5e1',
            fontSize: '0.8rem',
            cursor: 'pointer',
          }}
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          <span>{copied ? 'Copied Table' : 'Copy Markdown Table'}</span>
        </button>
      </div>

      {/* Focus Filter Pills */}
      <div style={{ display: 'flex', gap: '8px' }}>
        {['all', 'methodology', 'benchmarks', 'limitations'].map((f) => (
          <button
            key={f}
            onClick={() => setFilterFocus(f)}
            style={{
              padding: '4px 12px',
              borderRadius: '20px',
              fontSize: '0.75rem',
              fontWeight: 500,
              textTransform: 'capitalize',
              border: 'none',
              cursor: 'pointer',
              backgroundColor: filterFocus === f ? 'var(--accent-purple)' : 'rgba(30, 41, 59, 0.6)',
              color: filterFocus === f ? '#ffffff' : '#94a3b8',
            }}
          >
            {f === 'all' ? 'All Dimensions' : f}
          </button>
        ))}
      </div>

      {/* Comparative Cards / Table */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${Math.min(matrix.papers.length, 3)}, minmax(280px, 1fr))`,
          gap: '16px',
          overflowX: 'auto',
          paddingBottom: '8px',
        }}
      >
        {matrix.papers.map((paper, idx) => (
          <div
            key={idx}
            style={{
              backgroundColor: 'rgba(15, 23, 42, 0.7)',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            <div style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px' }}>
              <span
                style={{
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  color: 'var(--accent-purple)',
                  textTransform: 'uppercase',
                }}
              >
                Paper #{idx + 1}
              </span>
              <h4 style={{ margin: '4px 0 0 0', fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc' }}>
                {paper.title}
              </h4>
            </div>

            {/* Architecture Dimension */}
            {(filterFocus === 'all' || filterFocus === 'methodology') && (
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                  Architecture & Method
                </span>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.4' }}>
                  {typeof paper.methodology === 'string' ? paper.methodology : JSON.stringify(paper.methodology)}
                </p>
              </div>
            )}

            {/* Benchmarks Dimension */}
            {(filterFocus === 'all' || filterFocus === 'benchmarks') && (
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                  Datasets & Results
                </span>
                <div style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#cbd5e1' }}>
                  {Array.isArray(paper.benchmarks) && paper.benchmarks.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '6px' }}>
                      {paper.benchmarks.map((b, i) => (
                        <span
                          key={i}
                          style={{
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '0.7rem',
                            backgroundColor: 'rgba(56, 189, 248, 0.15)',
                            color: 'var(--accent-blue)',
                          }}
                        >
                          {String(b)}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p style={{ margin: 0, lineHeight: '1.4' }}>{String(paper.benchmarks || 'N/A')}</p>
                  )}
                  {paper.results && (
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>
                      <strong>Results:</strong> {typeof paper.results === 'object' ? JSON.stringify(paper.results) : String(paper.results)}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Limitations Dimension */}
            {(filterFocus === 'all' || filterFocus === 'limitations') && (
              <div
                style={{
                  backgroundColor: 'rgba(245, 158, 11, 0.05)',
                  border: '1px solid rgba(245, 158, 11, 0.2)',
                  borderRadius: '6px',
                  padding: '10px',
                }}
              >
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-amber)', textTransform: 'uppercase' }}>
                  Stated Limitations
                </span>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: '#cbd5e1', lineHeight: '1.4' }}>
                  {paper.limitations || 'None stated in paper.'}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
export default ComparisonMatrix
