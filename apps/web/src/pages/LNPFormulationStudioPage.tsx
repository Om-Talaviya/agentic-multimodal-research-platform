import React, { useState, useEffect } from 'react'
import {
  Boxes,
  CircleDot,
  RefreshCw,
  AlertCircle,
  Cpu,
  Layers,
  Activity,
  Sliders,
  Sparkles,
  Zap,
  TrendingDown,
  ShieldAlert
} from 'lucide-react'
import { api } from '../services/api'

interface LipidComponent {
  id: string
  component_name: string
  lipid_category: string
  molar_percentage: number
  molecular_weight_g_mol: number
  charge_at_ph7: number
}

interface MembraneProfile {
  id: string
  membrane_thickness_angstrom: number
  area_per_lipid_angstrom2: number
  order_parameter_s2: number
  bending_modulus_kc_kbt: number
  endosomal_escape_efficiency_pct: number
  cytotoxicity_score: number
}

interface LNPFormulation {
  id: string
  formulation_name: string
  cargo_type: string
  ionizable_lipid_name: string
  lipid_ratio_molar: Record<string, number>
  np_ratio: number
  encapsulation_efficiency_pct: number
  mean_diameter_nm: number
  pdi_polydispersity_index: number
  zeta_potential_mv: number
  apparent_pka: number
  metadata?: Record<string, any>
  components: LipidComponent[]
  membrane_profile: MembraneProfile | null
}

export const LNPFormulationStudioPage: React.FC = () => {
  const [formulations, setFormulations] = useState<LNPFormulation[]>([])
  const [selectedFormulation, setSelectedFormulation] = useState<LNPFormulation | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Form parameters
  const [name, setName] = useState('mRNA-LNP Benchmark Delivery Vehicle')
  const [cargo, setCargo] = useState('mRNA')
  const [ionizableLipid, setIonizableLipid] = useState('ALC-0315')
  const [npRatio, setNpRatio] = useState(6.0)
  const [frr, setFrr] = useState(3.0)
  const [tfr, setTfr] = useState(12.0)
  const [submitting, setSubmitting] = useState(false)

  const fetchFormulations = async () => {
    try {
      setLoading(true)
      const res = await api.get('/lnp/formulations')
      setFormulations(res.data)
      if (res.data.length > 0) {
        fetchFormulationDetails(res.data[0].id)
      } else {
        setLoading(false)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch LNP formulations')
      setLoading(false)
    }
  }

  const fetchFormulationDetails = async (id: string) => {
    try {
      const res = await api.get(`/lnp/formulations/${id}`)
      setSelectedFormulation(res.data)
      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch formulation details')
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFormulations()
  }, [])

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await api.post('/lnp/formulations/simulate', {
        formulation_name: name,
        cargo_type: cargo,
        ionizable_lipid_name: ionizableLipid,
        np_ratio: npRatio,
        flow_rate_ratio_aqueous_organic: frr,
        total_flow_rate_ml_min: tfr,
      })
      setSelectedFormulation(res.data)
      fetchFormulations()
    } catch (err: any) {
      setError(err.message || 'Simulation failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px', color: '#06b6d4' }}>
            <Boxes size={32} />
            Synthetic Cell Membrane & LNP Formulation Simulator
          </h1>
          <p style={{ color: 'var(--color-text-secondary, #94a3b8)', marginTop: '4px' }}>
            Microfluidic Self-Assembly Dynamics, Apparent pKa Optimization, Encapsulation Efficiency & Endosomal Escape Modeling
          </p>
        </div>
        <button
          onClick={fetchFormulations}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            borderRadius: '8px',
            backgroundColor: 'var(--color-surface, #1e293b)',
            border: '1px solid var(--color-border, #334155)',
            color: '#f8fafc',
            cursor: 'pointer'
          }}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div style={{ padding: '12px 16px', backgroundColor: '#ef444420', border: '1px solid #ef4444', borderRadius: '8px', color: '#fca5a5', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '24px' }}>
        {/* Left Column: Form & Recent Formulations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sliders size={20} color="#06b6d4" />
              Microfluidic Mixing Parameters
            </h3>
            <form onSubmit={handleSimulate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Formulation Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Cargo Type</label>
                  <select
                    value={cargo}
                    onChange={(e) => setCargo(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  >
                    <option value="mRNA">mRNA</option>
                    <option value="siRNA">siRNA</option>
                    <option value="pDNA">pDNA</option>
                    <option value="sgRNA">sgRNA</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Ionizable Lipid</label>
                  <select
                    value={ionizableLipid}
                    onChange={(e) => setIonizableLipid(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  >
                    <option value="ALC-0315">ALC-0315</option>
                    <option value="SM-102">SM-102</option>
                    <option value="MC3 (DLin-MC3-DMA)">MC3 (DLin-MC3)</option>
                    <option value="C12-200">C12-200</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>N/P Ratio (Charge Neutralization)</span>
                  <span style={{ color: '#06b6d4', fontWeight: 600 }}>{npRatio}</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={15}
                  step={0.5}
                  value={npRatio}
                  onChange={(e) => setNpRatio(Number(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Flow Rate Ratio (FRR)</label>
                  <input
                    type="number"
                    step={0.1}
                    min={1}
                    max={10}
                    value={frr}
                    onChange={(e) => setFrr(Number(e.target.value))}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Total Flow (mL/min)</label>
                  <input
                    type="number"
                    step={0.5}
                    min={1}
                    max={40}
                    value={tfr}
                    onChange={(e) => setTfr(Number(e.target.value))}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                style={{
                  marginTop: '8px',
                  padding: '10px',
                  borderRadius: '6px',
                  background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
                  color: '#fff',
                  fontWeight: 600,
                  border: 'none',
                  cursor: submitting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {submitting ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
                {submitting ? 'Simulating Self-Assembly...' : 'Simulate LNP Self-Assembly'}
              </button>
            </form>
          </div>

          {/* Formulations Catalog */}
          <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)', maxHeight: '380px', overflowY: 'auto' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} color="#38bdf8" />
              Formulation Candidates
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {formulations.map((f) => (
                <div
                  key={f.id}
                  onClick={() => fetchFormulationDetails(f.id)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    background: selectedFormulation?.id === f.id ? '#06b6d420' : '#0f172a',
                    border: selectedFormulation?.id === f.id ? '1px solid #06b6d4' : '1px solid #334155',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '14px', color: '#f8fafc' }}>{f.formulation_name}</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>{f.ionizable_lipid_name} • {f.cargo_type}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '11px', color: '#06b6d4' }}>
                    <span>Size: {f.mean_diameter_nm} nm</span>
                    <span>EE%: {f.encapsulation_efficiency_pct}%</span>
                  </div>
                </div>
              ))}
              {formulations.length === 0 && !loading && (
                <div style={{ textAlign: 'center', color: '#64748b', padding: '20px' }}>No formulations simulated</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Physical Chemistry & Membrane Dynamics */}
        {selectedFormulation ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Top Metric Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Hydrodynamic Diameter</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#06b6d4', marginTop: '4px' }}>
                  {selectedFormulation.mean_diameter_nm} nm
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>PDI: {selectedFormulation.pdi_polydispersity_index} (Monodisperse)</span>
              </div>

              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Encapsulation (EE%)</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981', marginTop: '4px' }}>
                  {selectedFormulation.encapsulation_efficiency_pct}%
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>RiboGreen Assay Simulation</span>
              </div>

              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Apparent pKa</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b', marginTop: '4px' }}>
                  {selectedFormulation.apparent_pka}
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Optimal Window (6.2 - 6.8)</span>
              </div>

              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Endosomal Escape</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#a855f7', marginTop: '4px' }}>
                  {selectedFormulation.membrane_profile?.endosomal_escape_efficiency_pct || 18.5}%
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Cytosolic Release Rate</span>
              </div>
            </div>

            {/* Lipid Composition 4-Way Breakdown */}
            <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CircleDot size={20} color="#06b6d4" />
                Lipid Composition & Molar Fractions
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
                {selectedFormulation.components?.map((c) => (
                  <div key={c.id} style={{ backgroundColor: '#0f172a', padding: '14px', borderRadius: '8px', border: '1px solid #334155' }}>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>{c.lipid_category.replace('_', ' ')}</div>
                    <div style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>{c.component_name}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                      <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#06b6d4' }}>{c.molar_percentage}%</span>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>MW: {c.molecular_weight_g_mol}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Membrane Biophysics & Dynamics Profile */}
            {selectedFormulation.membrane_profile && (
              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Activity size={20} color="#10b981" />
                  Synthetic Bilayer Dynamics & Biophysical Telemetry
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                  <div style={{ backgroundColor: '#0f172a', padding: '14px', borderRadius: '8px', border: '1px solid #334155' }}>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>Bilayer Thickness</span>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#f8fafc', marginTop: '4px' }}>
                      {selectedFormulation.membrane_profile.membrane_thickness_angstrom} Å
                    </div>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>Lipid Tail Packing</span>
                  </div>

                  <div style={{ backgroundColor: '#0f172a', padding: '14px', borderRadius: '8px', border: '1px solid #334155' }}>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>Area Per Lipid</span>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#f8fafc', marginTop: '4px' }}>
                      {selectedFormulation.membrane_profile.area_per_lipid_angstrom2} Å²
                    </div>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>Interfacial Area</span>
                  </div>

                  <div style={{ backgroundColor: '#0f172a', padding: '14px', borderRadius: '8px', border: '1px solid #334155' }}>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>Bending Rigidity (κc)</span>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#f8fafc', marginTop: '4px' }}>
                      {selectedFormulation.membrane_profile.bending_modulus_kc_kbt} kBT
                    </div>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>Membrane Flexibility</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', backgroundColor: 'var(--color-surface, #1e293b)', borderRadius: '12px', border: '1px solid var(--color-border, #334155)', color: '#64748b' }}>
            Select or simulate an LNP formulation to inspect biophysical properties
          </div>
        )}
      </div>
    </div>
  )
}

export default LNPFormulationStudioPage
