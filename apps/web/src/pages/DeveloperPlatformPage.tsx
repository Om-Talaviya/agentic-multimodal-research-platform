import React, { useState, useEffect } from 'react';
import {
  Key,
  Shield,
  Plus,
  Copy,
  Check,
  Trash2,
  Ban,
  RefreshCw,
  Code2,
  Terminal,
  Zap,
} from 'lucide-react';
import { DeveloperApiKey, CreateApiKeyPayload, ApiKeyCreatedResponse } from '../types/developer';

export const DeveloperPlatformPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'keys' | 'docs' | 'ratelimits'>('keys');
  const [apiKeys, setApiKeys] = useState<DeveloperApiKey[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Key creation modal state
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [keyName, setKeyName] = useState<string>('');
  const [selectedTier, setSelectedTier] = useState<'free' | 'pro' | 'enterprise'>('free');
  const [selectedScopes, setSelectedScopes] = useState<string[]>([
    'research:read',
    'research:write',
    'documents:read',
    'documents:write',
  ]);
  const [expirationDays, setExpirationDays] = useState<number>(90);
  const [creating, setCreating] = useState<boolean>(false);

  // Created secret key modal state
  const [newKeyData, setNewKeyData] = useState<ApiKeyCreatedResponse | null>(null);
  const [copiedSecret, setCopiedSecret] = useState<boolean>(false);

  // Docs playground state
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>('research_create');
  const [selectedLang, setSelectedLang] = useState<'curl' | 'python' | 'ts'>('curl');
  const [copiedCode, setCopiedCode] = useState<boolean>(false);

  const availableScopes = [
    { id: 'research:read', label: 'research:read', desc: 'Query research jobs and reports' },
    { id: 'research:write', label: 'research:write', desc: 'Trigger autonomous research workflows' },
    { id: 'documents:read', label: 'documents:read', desc: 'Search and read knowledge docs' },
    { id: 'documents:write', label: 'documents:write', desc: 'Ingest raw text/documents' },
    { id: 'memory:read', label: 'memory:read', desc: 'Recall cross-session research memories' },
    { id: 'graph:read', label: 'graph:read', desc: 'Query entity-relationship knowledge graph' },
  ];

  const fetchKeys = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/developer/keys', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`Failed to load developer keys: ${res.statusText}`);
      const data = await res.json();
      setApiKeys(data);
    } catch (err: any) {
      setError(err.message || 'Error loading developer API keys.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleCreateKey = async () => {
    if (!keyName.trim()) return;
    setCreating(true);
    try {
      const token = localStorage.getItem('token');
      const payload: CreateApiKeyPayload = {
        name: keyName.trim(),
        scopes: selectedScopes,
        rate_limit_tier: selectedTier,
        expires_in_days: expirationDays > 0 ? expirationDays : null,
      };

      const res = await fetch('/api/v1/developer/keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Failed to generate Developer API Key');
      const result: ApiKeyCreatedResponse = await res.json();
      setNewKeyData(result);
      setShowCreateModal(false);
      setKeyName('');
      fetchKeys();
    } catch (err: any) {
      alert(err.message || 'Error generating key');
    } finally {
      setCreating(false);
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key? Applications using it will be denied access.')) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/developer/keys/${keyId}/revoke`, {
        method: 'PATCH',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Failed to revoke API key');
      fetchKeys();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Permanently delete this API key record? This action cannot be undone.')) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/developer/keys/${keyId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Failed to delete API key');
      fetchKeys();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const toggleScope = (scopeId: string) => {
    if (selectedScopes.includes(scopeId)) {
      setSelectedScopes(selectedScopes.filter(s => s !== scopeId));
    } else {
      setSelectedScopes([...selectedScopes, scopeId]);
    }
  };

  const getCodeSnippet = () => {
    const keyPlaceholder = 'amrp_live_your_api_key_here';
    if (selectedEndpoint === 'research_create') {
      if (selectedLang === 'curl') {
        return `curl -X POST https://api.research-os.ai/api/v1/developer/research \\
  -H "X-API-Key: ${keyPlaceholder}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "What are the latest breakthroughs in high-temperature superconducting materials?",
    "routing_profile": "quality_maximized",
    "constraints": ["Cite papers from 2025-2026", "Provide quantitative Tc values"]
  }'`;
      } else if (selectedLang === 'python') {
        return `import requests

API_KEY = "${keyPlaceholder}"
BASE_URL = "https://api.research-os.ai/api/v1/developer"

response = requests.post(
    f"{BASE_URL}/research",
    headers={"X-API-Key": API_KEY},
    json={
        "question": "What are the latest breakthroughs in high-temperature superconducting materials?",
        "routing_profile": "quality_maximized",
        "constraints": ["Cite papers from 2025-2026", "Provide quantitative Tc values"]
    }
)

job = response.json()
print(f"Research Job Enqueued! Job ID: {job['job_id']}")
print(f"Poll URL: {job['poll_url']}")`;
      } else {
        return `import axios from 'axios';

const API_KEY = '${keyPlaceholder}';
const BASE_URL = 'https://api.research-os.ai/api/v1/developer';

async function startResearch() {
  const response = await axios.post(
    \`\${BASE_URL}/research\`,
    {
      question: 'What are the latest breakthroughs in high-temperature superconducting materials?',
      routing_profile: 'quality_maximized',
      constraints: ['Cite papers from 2025-2026', 'Provide quantitative Tc values'],
    },
    {
      headers: { 'X-API-Key': API_KEY }
    }
  );

  console.log('Enqueued Job ID:', response.data.job_id);
}

startResearch();`;
      }
    } else if (selectedEndpoint === 'research_poll') {
      if (selectedLang === 'curl') {
        return `curl -X GET https://api.research-os.ai/api/v1/developer/research/c8b3e1a0-4b2a-4311-9a70-fae9b3891823 \\
  -H "X-API-Key: ${keyPlaceholder}"`;
      } else if (selectedLang === 'python') {
        return `import requests

API_KEY = "${keyPlaceholder}"
JOB_ID = "c8b3e1a0-4b2a-4311-9a70-fae9b3891823"

res = requests.get(
    f"https://api.research-os.ai/api/v1/developer/research/{JOB_ID}",
    headers={"X-API-Key": API_KEY}
)
data = res.json()
print(f"Status: {data['status']}")
if data['report']:
    print("Synthesized Report Title:", data['report']['title'])`;
      } else {
        return `import axios from 'axios';

const API_KEY = '${keyPlaceholder}';
const JOB_ID = 'c8b3e1a0-4b2a-4311-9a70-fae9b3891823';

const res = await axios.get(
  \`https://api.research-os.ai/api/v1/developer/research/\${JOB_ID}\`,
  { headers: { 'X-API-Key': API_KEY } }
);

console.log('Report Title:', res.data.report?.title);`;
      }
    } else {
      if (selectedLang === 'curl') {
        return `curl -X POST https://api.research-os.ai/api/v1/developer/documents \\
  -H "X-API-Key: ${keyPlaceholder}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Quantum Computing Roadmap 2026",
    "content": "Recent benchmarks in neutral-atom quantum processors demonstrate 1200 physical qubits...",
    "source_type": "text"
  }'`;
      } else if (selectedLang === 'python') {
        return `import requests

API_KEY = "${keyPlaceholder}"

res = requests.post(
    "https://api.research-os.ai/api/v1/developer/documents",
    headers={"X-API-Key": API_KEY},
    json={
        "title": "Quantum Computing Roadmap 2026",
        "content": "Recent benchmarks in neutral-atom quantum processors demonstrate 1200 physical qubits...",
        "source_type": "text"
    }
)
print("Ingested Document ID:", res.json()["document_id"])`;
      } else {
        return `import axios from 'axios';

const API_KEY = '${keyPlaceholder}';

const res = await axios.post(
  'https://api.research-os.ai/api/v1/developer/documents',
  {
    title: 'Quantum Computing Roadmap 2026',
    content: 'Recent benchmarks in neutral-atom quantum processors demonstrate 1200 physical qubits...',
    source_type: 'text',
  },
  { headers: { 'X-API-Key': API_KEY } }
);

console.log('Ingested Document ID:', res.data.document_id);`;
      }
    }
  };

  const copyToClipboard = (text: string, isSecret = false) => {
    navigator.clipboard.writeText(text);
    if (isSecret) {
      setCopiedSecret(true);
      setTimeout(() => setCopiedSecret(false), 2000);
    } else {
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2000);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem', color: 'var(--text-primary)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ padding: '0.6rem', borderRadius: '10px', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Code2 size={26} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.75rem', fontWeight: '700', margin: 0 }}>Developer Platform & Public API</h1>
              <p style={{ margin: '0.25rem 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Manage API keys, inspect programmatic endpoints, and integrate the AI Research OS into external software.
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={fetchKeys}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.5rem 0.9rem',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={16} /> Refresh
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              border: 'none',
              background: 'var(--accent)',
              color: '#fff',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            <Plus size={16} /> Create API Key
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem' }}>
        <button
          onClick={() => setActiveTab('keys')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'keys' ? '2px solid var(--accent)' : '2px solid transparent',
            color: activeTab === 'keys' ? 'var(--accent)' : 'var(--text-secondary)',
            fontWeight: activeTab === 'keys' ? '600' : '400',
            cursor: 'pointer',
          }}
        >
          <Key size={16} /> API Keys ({apiKeys.length})
        </button>

        <button
          onClick={() => setActiveTab('docs')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'docs' ? '2px solid var(--accent)' : '2px solid transparent',
            color: activeTab === 'docs' ? 'var(--accent)' : 'var(--text-secondary)',
            fontWeight: activeTab === 'docs' ? '600' : '400',
            cursor: 'pointer',
          }}
        >
          <Terminal size={16} /> API Playground & SDK
        </button>

        <button
          onClick={() => setActiveTab('ratelimits')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'ratelimits' ? '2px solid var(--accent)' : '2px solid transparent',
            color: activeTab === 'ratelimits' ? 'var(--accent)' : 'var(--text-secondary)',
            fontWeight: activeTab === 'ratelimits' ? '600' : '400',
            cursor: 'pointer',
          }}
        >
          <Zap size={16} /> Rate Limits & Quotas
        </button>
      </div>

      {/* TAB 1: API Keys */}
      {activeTab === 'keys' && (
        <div>
          {/* Key Stat Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ padding: '1.25rem', borderRadius: '10px', background: 'var(--card-bg)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Total API Keys</div>
              <div style={{ fontSize: '1.75rem', fontWeight: '700', marginTop: '0.25rem' }}>{apiKeys.length}</div>
            </div>
            <div style={{ padding: '1.25rem', borderRadius: '10px', background: 'var(--card-bg)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Active Keys</div>
              <div style={{ fontSize: '1.75rem', fontWeight: '700', marginTop: '0.25rem', color: 'var(--success)' }}>
                {apiKeys.filter(k => k.is_active).length}
              </div>
            </div>
            <div style={{ padding: '1.25rem', borderRadius: '10px', background: 'var(--card-bg)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Authentication Standard</div>
              <div style={{ fontSize: '1.2rem', fontWeight: '600', marginTop: '0.25rem', color: '#38bdf8' }}>
                SHA-256 Hashed
              </div>
            </div>
          </div>

          {/* Keys Table */}
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '10px', overflow: 'hidden' }}>
            <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>Active API Keys</h3>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Prefix matching & secure constant-time validation</span>
            </div>

            {loading ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading developer keys...</div>
            ) : error ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--danger)' }}>{error}</div>
            ) : apiKeys.length === 0 ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                <Key size={36} style={{ opacity: 0.4, marginBottom: '0.5rem' }} />
                <p>No API keys generated yet. Click "Create API Key" to get started.</p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.02)' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Key Name</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Masked Key</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Tier</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Scopes</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Last Used</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {apiKeys.map(k => (
                      <tr key={k.id} style={{ borderBottom: '1px solid var(--border)' }}>
                        <td style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>{k.name}</td>
                        <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', color: '#38bdf8' }}>{k.masked_key}</td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <span
                            style={{
                              padding: '0.2rem 0.6rem',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              background: k.rate_limit_tier === 'enterprise' ? 'rgba(168, 85, 247, 0.2)' : 'rgba(56, 189, 248, 0.15)',
                              color: k.rate_limit_tier === 'enterprise' ? '#c084fc' : '#38bdf8',
                              textTransform: 'uppercase',
                            }}
                          >
                            {k.rate_limit_tier} ({k.rate_limit_rpm} rpm)
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap' }}>
                            {k.scopes.slice(0, 3).map(s => (
                              <span key={s} style={{ fontSize: '0.75rem', padding: '0.1rem 0.4rem', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>
                                {s}
                              </span>
                            ))}
                            {k.scopes.length > 3 && (
                              <span style={{ fontSize: '0.75rem', padding: '0.1rem 0.4rem', color: 'var(--text-secondary)' }}>
                                +{k.scopes.length - 3} more
                              </span>
                            )}
                          </div>
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <span
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.3rem',
                              fontSize: '0.8rem',
                              color: k.is_active ? 'var(--success)' : 'var(--danger)',
                            }}
                          >
                            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: k.is_active ? 'var(--success)' : 'var(--danger)' }}></span>
                            {k.is_active ? 'Active' : 'Revoked'}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                          {k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : 'Never'}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                            {k.is_active && (
                              <button
                                onClick={() => handleRevokeKey(k.id)}
                                title="Revoke Key"
                                style={{
                                  padding: '0.35rem 0.6rem',
                                  borderRadius: '6px',
                                  border: '1px solid var(--border)',
                                  background: 'rgba(239, 68, 68, 0.1)',
                                  color: 'var(--danger)',
                                  cursor: 'pointer',
                                }}
                              >
                                <Ban size={14} />
                              </button>
                            )}
                            <button
                              onClick={() => handleDeleteKey(k.id)}
                              title="Delete Key Record"
                              style={{
                                padding: '0.35rem 0.6rem',
                                borderRadius: '6px',
                                border: '1px solid var(--border)',
                                background: 'transparent',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer',
                              }}
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: Docs & Playground */}
      {activeTab === 'docs' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(250px, 300px) 1fr', gap: '1.5rem' }}>
          {/* Endpoint Selector Sidebar */}
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '10px', padding: '1rem' }}>
            <h4 style={{ margin: '0 0 0.75rem', fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Endpoints</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <button
                onClick={() => setSelectedEndpoint('research_create')}
                style={{
                  textAlign: 'left',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid',
                  borderColor: selectedEndpoint === 'research_create' ? 'var(--accent)' : 'transparent',
                  background: selectedEndpoint === 'research_create' ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                  color: selectedEndpoint === 'research_create' ? '#38bdf8' : 'var(--text-primary)',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--success)' }}>POST</div>
                <div style={{ fontSize: '0.85rem', fontWeight: '500' }}>/api/v1/developer/research</div>
              </button>

              <button
                onClick={() => setSelectedEndpoint('research_poll')}
                style={{
                  textAlign: 'left',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid',
                  borderColor: selectedEndpoint === 'research_poll' ? 'var(--accent)' : 'transparent',
                  background: selectedEndpoint === 'research_poll' ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                  color: selectedEndpoint === 'research_poll' ? '#38bdf8' : 'var(--text-primary)',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#38bdf8' }}>GET</div>
                <div style={{ fontSize: '0.85rem', fontWeight: '500' }}>/api/v1/developer/research/:id</div>
              </button>

              <button
                onClick={() => setSelectedEndpoint('documents_create')}
                style={{
                  textAlign: 'left',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid',
                  borderColor: selectedEndpoint === 'documents_create' ? 'var(--accent)' : 'transparent',
                  background: selectedEndpoint === 'documents_create' ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                  color: selectedEndpoint === 'documents_create' ? '#38bdf8' : 'var(--text-primary)',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--success)' }}>POST</div>
                <div style={{ fontSize: '0.85rem', fontWeight: '500' }}>/api/v1/developer/documents</div>
              </button>
            </div>
          </div>

          {/* Playground Code Display */}
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '10px', padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {(['curl', 'python', 'ts'] as const).map(lang => (
                  <button
                    key={lang}
                    onClick={() => setSelectedLang(lang)}
                    style={{
                      padding: '0.35rem 0.8rem',
                      borderRadius: '6px',
                      border: '1px solid var(--border)',
                      background: selectedLang === lang ? 'var(--accent)' : 'transparent',
                      color: selectedLang === lang ? '#fff' : 'var(--text-secondary)',
                      fontWeight: '600',
                      fontSize: '0.8rem',
                      cursor: 'pointer',
                      textTransform: 'uppercase',
                    }}
                  >
                    {lang === 'ts' ? 'TypeScript' : lang === 'python' ? 'Python' : 'cURL'}
                  </button>
                ))}
              </div>

              <button
                onClick={() => copyToClipboard(getCodeSnippet())}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.35rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'transparent',
                  color: 'var(--text-primary)',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                }}
              >
                {copiedCode ? <Check size={14} color="var(--success)" /> : <Copy size={14} />}
                {copiedCode ? 'Copied' : 'Copy Code'}
              </button>
            </div>

            <pre
              style={{
                background: '#090d16',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                padding: '1.25rem',
                color: '#e2e8f0',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                lineHeight: '1.5',
                overflowX: 'auto',
              }}
            >
              {getCodeSnippet()}
            </pre>
          </div>
        </div>
      )}

      {/* TAB 3: Rate Limits & Quotas */}
      {activeTab === 'ratelimits' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '10px', padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              <Zap size={18} />
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-primary)' }}>Free Developer Tier</h3>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', margin: '0.5rem 0' }}>60 <span style={{ fontSize: '1rem', fontWeight: '400', color: 'var(--text-secondary)' }}>req / min</span></div>
            <ul style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', paddingLeft: '1.2rem' }}>
              <li>Full Multi-Agent Research DAG access</li>
              <li>Hybrid Vector / BM25 document search</li>
              <li>Sliding 60-second window rate throttling</li>
            </ul>
          </div>

          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--accent)', borderRadius: '10px', padding: '1.5rem', position: 'relative' }}>
            <span style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'var(--accent)', color: '#fff', fontSize: '0.7rem', fontWeight: '700', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>RECOMMENDED</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#38bdf8', marginBottom: '0.5rem' }}>
              <Zap size={18} />
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-primary)' }}>Pro Tier</h3>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', margin: '0.5rem 0' }}>300 <span style={{ fontSize: '1rem', fontWeight: '400', color: 'var(--text-secondary)' }}>req / min</span></div>
            <ul style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', paddingLeft: '1.2rem' }}>
              <li>Priority asynchronous worker execution</li>
              <li>Higher multimodal audio/video throughput</li>
              <li>Dedicated rate limit bucket per API key</li>
            </ul>
          </div>

          <div style={{ background: 'var(--card-bg)', border: '1px solid rgba(168, 85, 247, 0.4)', borderRadius: '10px', padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#c084fc', marginBottom: '0.5rem' }}>
              <Shield size={18} />
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-primary)' }}>Enterprise Tier</h3>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', margin: '0.5rem 0' }}>1,200 <span style={{ fontSize: '1rem', fontWeight: '400', color: 'var(--text-secondary)' }}>req / min</span></div>
            <ul style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', paddingLeft: '1.2rem' }}>
              <li>Custom rate limits & dedicated cluster nodes</li>
              <li>KMS envelope encryption vault access</li>
              <li>SLA guarantees & 24/7 dedicated support</li>
            </ul>
          </div>
        </div>
      )}

      {/* MODAL: Generate API Key */}
      {showCreateModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
        >
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1.5rem', width: '100%', maxWidth: '520px' }}>
            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.25rem', fontWeight: '700' }}>Create Developer API Key</h3>
            <p style={{ margin: '0 0 1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Generate a cryptographically secure key with granular permission scopes.
            </p>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Key Name / Label</label>
              <input
                type="text"
                placeholder="e.g. Production Backend Service"
                value={keyName}
                onChange={e => setKeyName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Rate Limit Tier</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                {(['free', 'pro', 'enterprise'] as const).map(tier => (
                  <button
                    key={tier}
                    type="button"
                    onClick={() => setSelectedTier(tier)}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '6px',
                      border: '1px solid',
                      borderColor: selectedTier === tier ? 'var(--accent)' : 'var(--border)',
                      background: selectedTier === tier ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                      color: selectedTier === tier ? '#38bdf8' : 'var(--text-primary)',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      fontWeight: '600',
                      textTransform: 'capitalize',
                    }}
                  >
                    {tier}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Permission Scopes</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                {availableScopes.map(scope => {
                  const checked = selectedScopes.includes(scope.id);
                  return (
                    <div
                      key={scope.id}
                      onClick={() => toggleScope(scope.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 0.75rem',
                        borderRadius: '6px',
                        border: '1px solid',
                        borderColor: checked ? 'var(--accent)' : 'var(--border)',
                        background: checked ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                        cursor: 'pointer',
                        fontSize: '0.8rem',
                      }}
                    >
                      <input type="checkbox" checked={checked} readOnly style={{ cursor: 'pointer' }} />
                      <span>{scope.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Key Expiration</label>
              <select
                value={expirationDays}
                onChange={e => setExpirationDays(Number(e.target.value))}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                }}
              >
                <option value={30}>30 Days</option>
                <option value={60}>60 Days</option>
                <option value={90}>90 Days (Recommended)</option>
                <option value={180}>180 Days</option>
                <option value={365}>1 Year</option>
                <option value={0}>No Expiration (Never)</option>
              </select>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                onClick={() => setShowCreateModal(false)}
                style={{
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'transparent',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateKey}
                disabled={creating || !keyName.trim()}
                style={{
                  padding: '0.5rem 1.25rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: 'var(--accent)',
                  color: '#fff',
                  fontWeight: '600',
                  cursor: creating || !keyName.trim() ? 'not-allowed' : 'pointer',
                  opacity: creating || !keyName.trim() ? 0.6 : 1,
                }}
              >
                {creating ? 'Generating...' : 'Create Key'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Secret Key Reveal (One-Time) */}
      {newKeyData && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
        >
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--accent)', borderRadius: '12px', padding: '1.5rem', width: '100%', maxWidth: '520px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)', marginBottom: '0.5rem' }}>
              <Check size={20} />
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '700' }}>API Key Generated</h3>
            </div>
            <p style={{ margin: '0 0 1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Copy and store this secret key safely. For security reasons, <strong>you will not be able to view it again</strong>.
            </p>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <input
                type="text"
                readOnly
                value={newKeyData.secret_key}
                style={{
                  flex: 1,
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: '#090d16',
                  color: '#38bdf8',
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                }}
              />
              <button
                onClick={() => copyToClipboard(newKeyData.secret_key, true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  padding: '0.6rem 1rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: 'var(--accent)',
                  color: '#fff',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                {copiedSecret ? <Check size={16} /> : <Copy size={16} />}
                {copiedSecret ? 'Copied' : 'Copy'}
              </button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setNewKeyData(null)}
                style={{
                  padding: '0.5rem 1.25rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'var(--card-bg)',
                  color: 'var(--text-primary)',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                I Have Stored This Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
