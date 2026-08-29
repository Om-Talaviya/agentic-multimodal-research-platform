import { useState } from 'react'
import { Save, Loader2, CheckCircle, AlertCircle, Info } from 'lucide-react'

export function Settings() {
  const [settings, setSettings] = useState({
    ollama_url: 'http://localhost:11434',
    default_llm_model: 'llama3.1',
    default_vision_model: 'llava',
    default_embedding_model: 'nomic-embed-text',
    log_level: 'INFO',
    max_upload_size: 50,
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)
    try {
      // In a real app, this would save to backend config
      await new Promise(r => setTimeout(r, 1000))
      setMessage({ type: 'success', text: 'Settings saved successfully!' })
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save settings' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ maxWidth: '800px' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: 'var(--spacing-lg)' }}>
        Settings
      </h1>

      <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 'var(--spacing-lg)' }}>
          Model Providers
        </h2>
        
        <div style={{ display: 'grid', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-md)' }}>
            <div>
              <label className="label">Ollama URL</label>
              <input
                type="text"
                className="input"
                value={settings.ollama_url}
                onChange={e => setSettings(prev => ({ ...prev, ollama_url: e.target.value }))}
                placeholder="http://localhost:11434"
              />
            </div>
            <div>
              <label className="label">Default LLM Model</label>
              <select className="input" value={settings.default_llm_model} onChange={e => setSettings(prev => ({ ...prev, default_llm_model: e.target.value }))}>
                <option value="llama3.1">llama3.1</option>
                <option value="mistral">mistral</option>
                <option value="codellama">codellama</option>
              </select>
            </div>
            <div>
              <label className="label">Default Vision Model</label>
              <select className="input" value={settings.default_vision_model} onChange={e => setSettings(prev => ({ ...prev, default_vision_model: e.target.value }))}>
                <option value="llava">llava</option>
                <option value="bakllava">bakllava</option>
              </select>
            </div>
            <div>
              <label className="label">Default Embedding Model</label>
              <select className="input" value={settings.default_embedding_model} onChange={e => setSettings(prev => ({ ...prev, default_embedding_model: e.target.value }))}>
                <option value="nomic-embed-text">nomic-embed-text</option>
                <option value="all-minilm">all-minilm</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 'var(--spacing-md)', paddingTop: 'var(--spacing-md)', borderTop: '1px solid var(--color-border)' }}>
            <button onClick={handleSave} disabled={saving} className="btn btn-primary">
              {saving ? <Loader2 className="loading-spinner" /> : <> <Save size={18} /> Save Settings </>}
            </button>
            {message && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', padding: 'var(--spacing-sm) var(--spacing-md)', borderRadius: 'var(--radius-md)', background: message.type === 'success' ? '#d1fae5' : '#fee2e2', color: message.type === 'success' ? '#065f46' : '#991b1b' }}>
                {message.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
                {message.text}
              </div>
            )}
          </div>
        </div>

        <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--spacing-lg)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
            Available Models (Ollama)
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', color: 'var(--color-text-muted)' }}>
            <Info size={20} />
            <span>Configure models in Ollama: <code>ollama pull llama3.1</code></span>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 'var(--spacing-lg)' }}>
          General Settings
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-md)' }}>
          <div>
            <label className="label">Log Level</label>
            <select className="input" value={settings.log_level} onChange={e => setSettings(prev => ({ ...prev, log_level: e.target.value }))}>
              <option value="DEBUG">Debug</option>
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="ERROR">Error</option>
            </select>
          </div>
          <div>
            <label className="label">Max Upload Size (MB)</label>
            <input type="number" className="input" value={settings.max_upload_size} onChange={e => setSettings(prev => ({ ...prev, max_upload_size: parseInt(e.target.value) }))} min="1" max="500" />
          </div>
        </div>
      </div>
    </div>
  )
}