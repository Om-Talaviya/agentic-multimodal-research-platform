import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Code2,
  Copy,
  Download,
  Flame,
  FlaskConical,
  Layers,
  Play,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  Timer,
  Workflow,
} from 'lucide-react';
import { api } from '../services/api';

interface LabwareSlot {
  id?: string;
  slot_number: number;
  labware_type: string;
  reagent_name?: string;
  initial_volume_ul: number;
  current_volume_ul?: number;
}

interface LiquidTransferStep {
  id?: string;
  step_index: number;
  source_slot: number;
  source_well: string;
  target_slot: number;
  target_well: string;
  volume_ul: number;
  pipette_name: string;
  transfer_type: string;
  liquid_class: string;
}

interface CollisionWarning {
  step_index: number;
  warning_type: string;
  message: string;
  severity: string;
}

interface SimulationStepLog {
  step_index: number;
  action: string;
  details: string;
  source_remaining_ul: number;
  target_current_ul: number;
  tip_number: number;
  elapsed_time_sec: number;
}

interface ExecutionTrace {
  id: string;
  step_count: number;
  simulated_runtime_sec: number;
  estimated_tip_count: number;
  tip_waste_pct: number;
  collision_warnings: CollisionWarning[];
  simulation_log: SimulationStepLog[];
  executed_at?: string;
}

interface RoboticProtocol {
  id: string;
  protocol_name: string;
  robot_platform: string;
  assay_type: string;
  validation_status: string;
  total_runtime_minutes: number;
  liquid_waste_volume_ml: number;
  protocol_python_code?: string;
  pylabrobot_code?: string;
  autoprotocol_json?: any;
  deck_slots?: LabwareSlot[];
  transfer_steps?: LiquidTransferStep[];
  execution_traces?: ExecutionTrace[];
  created_at?: string;
}

export const LabAutomationPage: React.FC = () => {
  const [protocols, setProtocols] = useState<RoboticProtocol[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<RoboticProtocol | null>(null);
  const [activeTab, setActiveTab] = useState<'deck' | 'steps' | 'simulation' | 'code'>('deck');
  const [codeFormat, setCodeFormat] = useState<'opentrons' | 'pylabrobot' | 'autoprotocol'>('opentrons');
  const [loading, setLoading] = useState<boolean>(true);
  const [compiling, setCompiling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Form State for Compilation
  const [protocolName, setProtocolName] = useState('CRISPR-Cas9 LNP High-Throughput Formulation & Transfection');
  const [robotPlatform, setRobotPlatform] = useState('Opentrons_OT2');
  const [assayType, setAssayType] = useState('CRISPR_LNP_Formulation');
  const [selectedSlotNum, setSelectedSlotNum] = useState<number>(2);

  const fetchProtocols = async () => {
    try {
      setLoading(true);
      const res = await api.get('/lab/protocols');
      const list: RoboticProtocol[] = res.data || [];
      setProtocols(list);
      if (list.length > 0) {
        // Fetch full protocol details for the first one
        const fullRes = await api.get(`/lab/protocols/${list[0].id}`);
        setSelectedProtocol(fullRes.data);
      } else {
        setSelectedProtocol(null);
      }
      setError(null);
    } catch (err: any) {
      loggerError('Failed to fetch robotic protocols', err);
      setError('Unable to load robotic protocols. Verify backend connectivity.');
    } finally {
      setLoading(false);
    }
  };

  const selectProtocol = async (id: string) => {
    try {
      setLoading(true);
      const res = await api.get(`/lab/protocols/${id}`);
      setSelectedProtocol(res.data);
      setError(null);
    } catch (err: any) {
      setError('Failed to fetch protocol details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProtocols();
  }, []);

  const handleCompile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setCompiling(true);
      setError(null);
      const res = await api.post('/lab/protocols/compile', {
        protocol_name: protocolName,
        robot_platform: robotPlatform,
        assay_type: assayType,
      });

      const newProto = res.data;
      setProtocols((prev) => [newProto, ...prev]);
      setSelectedProtocol(newProto);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Compilation failed.');
    } finally {
      setCompiling(false);
    }
  };

  const handleCopyCode = () => {
    if (!selectedProtocol) return;
    let text = '';
    if (codeFormat === 'opentrons') {
      text = selectedProtocol.protocol_python_code || '';
    } else if (codeFormat === 'pylabrobot') {
      text = selectedProtocol.pylabrobot_code || '# PyLabRobot Universal script';
    } else {
      text = JSON.stringify(selectedProtocol.autoprotocol_json || {}, null, 2);
    }
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!selectedProtocol) return;
    let content = '';
    let filename = '';
    let mimeType = 'text/plain';

    if (codeFormat === 'opentrons') {
      content = selectedProtocol.protocol_python_code || '';
      filename = `${selectedProtocol.protocol_name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_opentrons.py`;
    } else if (codeFormat === 'pylabrobot') {
      content = selectedProtocol.pylabrobot_code || '';
      filename = `${selectedProtocol.protocol_name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_pylabrobot.py`;
    } else {
      content = JSON.stringify(selectedProtocol.autoprotocol_json || {}, null, 2);
      filename = `${selectedProtocol.protocol_name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_autoprotocol.json`;
      mimeType = 'application/json';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Helper to safely log errors
  const loggerError = (msg: string, err: any) => {
    console.error(msg, err);
  };

  // Deck slot grid map (12 slots for OT-2/Flex standard layout)
  // Standard Opentrons OT-2 Deck layout is 4 rows x 3 cols:
  // Top Row: 10, 11, 12
  // Row 3: 7, 8, 9
  // Row 2: 4, 5, 6
  // Bottom Row: 1, 2, 3
  const deckSlotsGrid = [
    [10, 11, 12],
    [7, 8, 9],
    [4, 5, 6],
    [1, 2, 3],
  ];

  const getSlotData = (slotNum: number) => {
    return selectedProtocol?.deck_slots?.find((s) => s.slot_number === slotNum);
  };

  const selectedSlot = selectedProtocol?.deck_slots?.find((s) => s.slot_number === selectedSlotNum);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', paddingBottom: '3rem' }}>
      {/* Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
          borderRadius: '1rem',
          padding: '1.75rem 2rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.36)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div
            style={{
              width: '3.5rem',
              height: '3.5rem',
              borderRadius: '1rem',
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(6, 182, 212, 0.4)',
            }}
          >
            <Bot size={28} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
                Robotic Lab Automation & Liquid Handling Studio
              </h1>
              <span
                style={{
                  background: 'rgba(6, 182, 212, 0.15)',
                  color: '#22d3ee',
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}
              >
                Generation 11 • Phase 37
              </span>
            </div>
            <p style={{ margin: '0.35rem 0 0 0', color: '#94a3b8', fontSize: '0.9rem', maxWidth: '750px' }}>
              Autonomous Opentrons OT-2 / Flex Python v2 compiler, 12-slot deck spatial collision solver, PyLabRobot Universal synthesis, and microfluidic liquid class execution.
            </p>
          </div>
        </div>

        <button
          onClick={fetchProtocols}
          disabled={loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.6rem 1rem',
            borderRadius: '0.5rem',
            backgroundColor: 'rgba(51, 65, 85, 0.8)',
            color: '#e2e8f0',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            cursor: 'pointer',
            fontWeight: 500,
            fontSize: '0.875rem',
            transition: 'all 0.2s',
          }}
        >
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          Refresh Deck
        </button>
      </div>

      {error && (
        <div
          style={{
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '0.75rem',
            padding: '1rem',
            color: '#fca5a5',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Studio Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Left Sidebar: Form & Protocols List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Synthesizer Card */}
          <div
            style={{
              backgroundColor: 'rgba(30, 41, 59, 0.7)',
              borderRadius: '0.75rem',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '1.25rem',
            }}
          >
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: 600, color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={16} color="#06b6d4" />
              Compile Robotic Protocol
            </h3>
            <form onSubmit={handleCompile} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                  Protocol Title
                </label>
                <input
                  type="text"
                  value={protocolName}
                  onChange={(e) => setProtocolName(e.target.value)}
                  style={{
                    width: '100%',
                    backgroundColor: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '0.375rem',
                    padding: '0.5rem 0.75rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                    boxSizing: 'border-box',
                  }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                  Workstation Platform
                </label>
                <select
                  value={robotPlatform}
                  onChange={(e) => setRobotPlatform(e.target.value)}
                  style={{
                    width: '100%',
                    backgroundColor: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '0.375rem',
                    padding: '0.5rem 0.75rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                    boxSizing: 'border-box',
                  }}
                >
                  <option value="Opentrons_OT2">Opentrons OT-2 (Gen2)</option>
                  <option value="Opentrons_Flex">Opentrons Flex (96/8-Ch)</option>
                  <option value="PyLabRobot_Universal">PyLabRobot Universal Backend</option>
                  <option value="Tecan_Fluent">Tecan Fluent 780</option>
                  <option value="Hamilton_STAR">Hamilton Microlab STAR</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                  Assay / Formulation Type
                </label>
                <select
                  value={assayType}
                  onChange={(e) => setAssayType(e.target.value)}
                  style={{
                    width: '100%',
                    backgroundColor: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '0.375rem',
                    padding: '0.5rem 0.75rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                    boxSizing: 'border-box',
                  }}
                >
                  <option value="CRISPR_LNP_Formulation">CRISPR LNP Microfluidic Formulation</option>
                  <option value="qPCR_Assay">qPCR Target Master Mix & Plating</option>
                  <option value="ELISA_Screening">High-Throughput ELISA Screening</option>
                  <option value="Serial_Dilution">12-Point IC50 Serial Dilution</option>
                  <option value="PCR_MasterMix">PCR Amplification & Normalization</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={compiling}
                style={{
                  backgroundColor: '#06b6d4',
                  color: '#0f172a',
                  border: 'none',
                  borderRadius: '0.375rem',
                  padding: '0.65rem 1rem',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  marginTop: '0.5rem',
                  transition: 'background-color 0.2s',
                }}
              >
                {compiling ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
                {compiling ? 'Compiling & Simulating...' : 'Compile & Simulate'}
              </button>
            </form>
          </div>

          {/* Protocols List Card */}
          <div
            style={{
              backgroundColor: 'rgba(30, 41, 59, 0.7)',
              borderRadius: '0.75rem',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '1.25rem',
              maxHeight: '400px',
              overflowY: 'auto',
            }}
          >
            <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.85rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
              Compiled Protocols ({protocols.length})
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {protocols.map((p) => {
                const isSelected = selectedProtocol?.id === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => selectProtocol(p.id)}
                    style={{
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.15)' : 'rgba(15, 23, 42, 0.5)',
                      border: isSelected ? '1px solid rgba(6, 182, 212, 0.4)' : '1px solid rgba(255, 255, 255, 0.05)',
                      cursor: 'pointer',
                      transition: 'all 0.15s',
                    }}
                  >
                    <div style={{ fontWeight: 600, fontSize: '0.85rem', color: isSelected ? '#38bdf8' : '#e2e8f0', marginBottom: '0.25rem' }}>
                      {p.protocol_name}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8' }}>
                      <span>{p.robot_platform}</span>
                      <span style={{ color: p.validation_status === 'valid' ? '#4ade80' : '#fbbf24' }}>
                        {p.validation_status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Main Deck Inspector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {selectedProtocol ? (
            <>
              {/* Telemetry Summary Header */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '1rem',
                }}
              >
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <Timer size={24} color="#38bdf8" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Estimated Runtime</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedProtocol.total_runtime_minutes.toFixed(1)} min
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <Flame size={24} color="#fb923c" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Liquid Waste Volume</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedProtocol.liquid_waste_volume_ml.toFixed(2)} mL
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <Layers size={24} color="#a855f7" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Deck Slots Used</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedProtocol.deck_slots?.length || 0} / 12 Slots
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <CheckCircle2 size={24} color="#4ade80" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Safety & Collision</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#4ade80', textTransform: 'capitalize' }}>
                      {selectedProtocol.validation_status}
                    </div>
                  </div>
                </div>
              </div>

              {/* Tab Navigation */}
              <div style={{ display: 'flex', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', gap: '1rem' }}>
                <button
                  onClick={() => setActiveTab('deck')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'deck' ? '2px solid #06b6d4' : '2px solid transparent',
                    color: activeTab === 'deck' ? '#38bdf8' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <Workflow size={16} />
                  12-Slot Deck Visualizer
                </button>

                <button
                  onClick={() => setActiveTab('steps')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'steps' ? '2px solid #06b6d4' : '2px solid transparent',
                    color: activeTab === 'steps' ? '#38bdf8' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <FlaskConical size={16} />
                  Transfer Steps ({selectedProtocol.transfer_steps?.length || 0})
                </button>

                <button
                  onClick={() => setActiveTab('simulation')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'simulation' ? '2px solid #06b6d4' : '2px solid transparent',
                    color: activeTab === 'simulation' ? '#38bdf8' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <ShieldAlert size={16} />
                  Physics & Collision Telemetry
                </button>

                <button
                  onClick={() => setActiveTab('code')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'code' ? '2px solid #06b6d4' : '2px solid transparent',
                    color: activeTab === 'code' ? '#38bdf8' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <Code2 size={16} />
                  Executable Code
                </button>
              </div>

              {/* Tab Content: 12-Slot Deck Visualizer */}
              {activeTab === 'deck' && (
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.7)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1.5rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc' }}>
                        Opentrons OT-2 / Flex Deck Grid Configuration
                      </h3>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>
                        Click any slot below to inspect labware geometry, reagent inventory, and well coordinate allocations.
                      </p>
                    </div>
                  </div>

                  {/* 4x3 Grid */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(3, 1fr)',
                      gap: '1rem',
                      backgroundColor: 'rgba(15, 23, 42, 0.8)',
                      padding: '1.25rem',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(255, 255, 255, 0.06)',
                    }}
                  >
                    {deckSlotsGrid.map((row) =>
                      row.map((slotNum) => {
                        const slotData = getSlotData(slotNum);
                        const isSelected = selectedSlotNum === slotNum;
                        return (
                          <div
                            key={slotNum}
                            onClick={() => setSelectedSlotNum(slotNum)}
                            style={{
                              minHeight: '110px',
                              backgroundColor: slotData
                                ? isSelected
                                  ? 'rgba(6, 182, 212, 0.2)'
                                  : 'rgba(30, 41, 59, 0.8)'
                                : 'rgba(15, 23, 42, 0.4)',
                              border: isSelected
                                ? '2px solid #06b6d4'
                                : slotData
                                ? '1px solid rgba(255, 255, 255, 0.15)'
                                : '1px dashed rgba(255, 255, 255, 0.05)',
                              borderRadius: '0.5rem',
                              padding: '0.75rem',
                              cursor: 'pointer',
                              display: 'flex',
                              flexDirection: 'column',
                              justifyContent: 'space-between',
                              transition: 'all 0.15s',
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span
                                style={{
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  color: isSelected ? '#22d3ee' : '#64748b',
                                  backgroundColor: 'rgba(0,0,0,0.3)',
                                  padding: '0.1rem 0.4rem',
                                  borderRadius: '0.25rem',
                                }}
                              >
                                Slot {slotNum}
                              </span>
                              {slotData && (
                                <span
                                  style={{
                                    fontSize: '0.65rem',
                                    color: '#38bdf8',
                                    fontWeight: 600,
                                  }}
                                >
                                  {slotData.initial_volume_ul} µL
                                </span>
                              )}
                            </div>

                            {slotData ? (
                              <div>
                                <div
                                  style={{
                                    fontSize: '0.8rem',
                                    fontWeight: 600,
                                    color: '#f8fafc',
                                    lineHeight: 1.2,
                                    marginBottom: '0.2rem',
                                  }}
                                >
                                  {slotData.reagent_name || slotData.labware_type}
                                </div>
                                <div style={{ fontSize: '0.7rem', color: '#94a3b8', wordBreak: 'break-all' }}>
                                  {slotData.labware_type}
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.75rem', color: '#475569', fontStyle: 'italic', textAlign: 'center' }}>
                                Empty Deck Slot
                              </div>
                            )}
                          </div>
                        );
                      })
                    )}
                  </div>

                  {/* Slot Details Banner */}
                  {selectedSlot && (
                    <div
                      style={{
                        marginTop: '1.25rem',
                        padding: '1rem',
                        backgroundColor: 'rgba(15, 23, 42, 0.6)',
                        borderRadius: '0.5rem',
                        border: '1px solid rgba(6, 182, 212, 0.2)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                          Selected Position: Slot {selectedSlot.slot_number}
                        </div>
                        <div style={{ fontSize: '1rem', fontWeight: 600, color: '#38bdf8' }}>
                          {selectedSlot.reagent_name || 'Generic Labware'}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                          Labware Definition: <code>{selectedSlot.labware_type}</code>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Initial Reagent Volume</div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#4ade80' }}>
                          {selectedSlot.initial_volume_ul} µL
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tab Content: Transfer Steps */}
              {activeTab === 'steps' && (
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.7)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1.5rem',
                  }}
                >
                  <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: '#f8fafc' }}>
                    Microfluidic Pipetting & Liquid Handling Operations
                  </h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: '#94a3b8' }}>
                          <th style={{ padding: '0.6rem' }}>#</th>
                          <th style={{ padding: '0.6rem' }}>Action</th>
                          <th style={{ padding: '0.6rem' }}>Source</th>
                          <th style={{ padding: '0.6rem' }}>Target</th>
                          <th style={{ padding: '0.6rem' }}>Volume</th>
                          <th style={{ padding: '0.6rem' }}>Pipette</th>
                          <th style={{ padding: '0.6rem' }}>Liquid Class</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedProtocol.transfer_steps?.map((step) => (
                          <tr
                            key={step.id || step.step_index}
                            style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: '#e2e8f0' }}
                          >
                            <td style={{ padding: '0.6rem', fontWeight: 600, color: '#38bdf8' }}>{step.step_index}</td>
                            <td style={{ padding: '0.6rem' }}>
                              <span
                                style={{
                                  backgroundColor: step.transfer_type === 'mix' ? 'rgba(168, 85, 247, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                                  color: step.transfer_type === 'mix' ? '#c084fc' : '#22d3ee',
                                  padding: '0.2rem 0.5rem',
                                  borderRadius: '0.25rem',
                                  fontSize: '0.75rem',
                                  fontWeight: 600,
                                }}
                              >
                                {step.transfer_type}
                              </span>
                            </td>
                            <td style={{ padding: '0.6rem' }}>
                              Slot {step.source_slot} [{step.source_well}]
                            </td>
                            <td style={{ padding: '0.6rem' }}>
                              Slot {step.target_slot} [{step.target_well}]
                            </td>
                            <td style={{ padding: '0.6rem', fontWeight: 600 }}>{step.volume_ul} µL</td>
                            <td style={{ padding: '0.6rem', color: '#94a3b8' }}>{step.pipette_name}</td>
                            <td style={{ padding: '0.6rem' }}>
                              <span
                                style={{
                                  color: step.liquid_class.includes('viscous') ? '#fbbf24' : '#93c5fd',
                                }}
                              >
                                {step.liquid_class}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab Content: Simulation & Physics Telemetry */}
              {activeTab === 'simulation' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {/* Warnings Panel */}
                  {selectedProtocol.execution_traces?.[0]?.collision_warnings &&
                  selectedProtocol.execution_traces[0].collision_warnings.length > 0 ? (
                    <div
                      style={{
                        backgroundColor: 'rgba(245, 158, 11, 0.15)',
                        border: '1px solid rgba(245, 158, 11, 0.3)',
                        borderRadius: '0.75rem',
                        padding: '1.25rem',
                      }}
                    >
                      <h4 style={{ margin: '0 0 0.75rem 0', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <AlertTriangle size={18} />
                        Spatial Collision & Volume Warning Telemetry
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {selectedProtocol.execution_traces[0].collision_warnings.map((w, idx) => (
                          <div
                            key={idx}
                            style={{
                              fontSize: '0.85rem',
                              color: '#fef3c7',
                              padding: '0.5rem 0.75rem',
                              backgroundColor: 'rgba(0,0,0,0.2)',
                              borderRadius: '0.375rem',
                            }}
                          >
                            <strong>[Step {w.step_index}] {w.warning_type}:</strong> {w.message}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div
                      style={{
                        backgroundColor: 'rgba(34, 197, 94, 0.15)',
                        border: '1px solid rgba(34, 197, 94, 0.3)',
                        borderRadius: '0.75rem',
                        padding: '1.25rem',
                        color: '#86efac',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                      }}
                    >
                      <CheckCircle2 size={20} />
                      <span>Zero collision risks detected. All deck trajectories clear and pipette volume limits verified.</span>
                    </div>
                  )}

                  {/* Step Execution Trace Log */}
                  <div
                    style={{
                      backgroundColor: 'rgba(30, 41, 59, 0.7)',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '1.5rem',
                    }}
                  >
                    <h4 style={{ margin: '0 0 1rem 0', color: '#f8fafc', fontSize: '1rem' }}>
                      Virtual Microfluidic Simulation Execution Log
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '350px', overflowY: 'auto' }}>
                      {selectedProtocol.execution_traces?.[0]?.simulation_log?.map((log, lIdx) => (
                        <div
                          key={lIdx}
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: '0.6rem 0.85rem',
                            borderRadius: '0.375rem',
                            backgroundColor: 'rgba(15, 23, 42, 0.6)',
                            fontSize: '0.8rem',
                            color: '#cbd5e1',
                          }}
                        >
                          <div>
                            <span style={{ color: '#38bdf8', fontWeight: 600, marginRight: '0.5rem' }}>
                              +{log.elapsed_time_sec.toFixed(1)}s
                            </span>
                            <span>{log.details}</span>
                          </div>
                          <div style={{ color: '#94a3b8' }}>
                            Src: {log.source_remaining_ul}µL | Tgt: {log.target_current_ul}µL | Tip #{log.tip_number}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab Content: Executable Code */}
              {activeTab === 'code' && (
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.7)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1.5rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    {/* Sub tabs for formats */}
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => setCodeFormat('opentrons')}
                        style={{
                          padding: '0.4rem 0.75rem',
                          borderRadius: '0.375rem',
                          backgroundColor: codeFormat === 'opentrons' ? '#06b6d4' : 'rgba(15, 23, 42, 0.6)',
                          color: codeFormat === 'opentrons' ? '#0f172a' : '#cbd5e1',
                          border: 'none',
                          fontWeight: 600,
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                        }}
                      >
                        Opentrons Python API v2
                      </button>
                      <button
                        onClick={() => setCodeFormat('pylabrobot')}
                        style={{
                          padding: '0.4rem 0.75rem',
                          borderRadius: '0.375rem',
                          backgroundColor: codeFormat === 'pylabrobot' ? '#06b6d4' : 'rgba(15, 23, 42, 0.6)',
                          color: codeFormat === 'pylabrobot' ? '#0f172a' : '#cbd5e1',
                          border: 'none',
                          fontWeight: 600,
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                        }}
                      >
                        PyLabRobot Universal
                      </button>
                      <button
                        onClick={() => setCodeFormat('autoprotocol')}
                        style={{
                          padding: '0.4rem 0.75rem',
                          borderRadius: '0.375rem',
                          backgroundColor: codeFormat === 'autoprotocol' ? '#06b6d4' : 'rgba(15, 23, 42, 0.6)',
                          color: codeFormat === 'autoprotocol' ? '#0f172a' : '#cbd5e1',
                          border: 'none',
                          fontWeight: 600,
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                        }}
                      >
                        Autoprotocol JSON
                      </button>
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={handleCopyCode}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          padding: '0.4rem 0.75rem',
                          backgroundColor: 'rgba(51, 65, 85, 0.8)',
                          color: '#f8fafc',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          fontWeight: 500,
                        }}
                      >
                        <Copy size={14} />
                        {copied ? 'Copied!' : 'Copy Code'}
                      </button>
                      <button
                        onClick={handleDownload}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          padding: '0.4rem 0.75rem',
                          backgroundColor: '#06b6d4',
                          color: '#0f172a',
                          border: 'none',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                        }}
                      >
                        <Download size={14} />
                        Download
                      </button>
                    </div>
                  </div>

                  <pre
                    style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      padding: '1.25rem',
                      borderRadius: '0.5rem',
                      color: '#38bdf8',
                      fontFamily: 'monospace',
                      fontSize: '0.8rem',
                      lineHeight: 1.5,
                      overflowX: 'auto',
                      maxHeight: '450px',
                      border: '1px solid rgba(255, 255, 255, 0.05)',
                    }}
                  >
                    <code>
                      {codeFormat === 'opentrons' && (selectedProtocol.protocol_python_code || '# No Python code generated')}
                      {codeFormat === 'pylabrobot' && (selectedProtocol.pylabrobot_code || '# PyLabRobot Universal script')}
                      {codeFormat === 'autoprotocol' && JSON.stringify(selectedProtocol.autoprotocol_json || {}, null, 2)}
                    </code>
                  </pre>
                </div>
              )}
            </>
          ) : (
            <div
              style={{
                backgroundColor: 'rgba(30, 41, 59, 0.7)',
                borderRadius: '0.75rem',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: '3rem',
                textAlign: 'center',
                color: '#94a3b8',
              }}
            >
              <Bot size={48} color="#06b6d4" style={{ margin: '0 auto 1rem auto', display: 'block' }} />
              <h3>No Robotic Protocol Selected</h3>
              <p>Compile a new protocol or select one from the catalog to inspect deck layout and code.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
