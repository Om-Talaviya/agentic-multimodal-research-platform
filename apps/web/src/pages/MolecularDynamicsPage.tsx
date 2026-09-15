import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  AlertCircle,
  Atom,
  Download,
  Gauge,
  Layers,
  Pause,
  Play,
  RefreshCw,
  RotateCcw,
  Zap,
  FileCode,
  TrendingUp,
} from 'lucide-react';
import { api } from '../services/api';

interface TrajectoryFrame {
  id: string;
  frame_index: number;
  timestamp_ps: number;
  rmsd_angstrom: number;
  radius_of_gyration_angstrom: number;
  potential_energy_kj_mol?: number;
  kinetic_energy_kj_mol?: number;
  total_energy_kj_mol?: number;
  temperature_kelvin?: number;
}

interface ResidueFluctuation {
  id: string;
  residue_number: number;
  residue_name: string;
  rmsf_angstrom: number;
  b_factor_equivalent: number;
  is_flexible_loop: boolean;
  secondary_structure_type: string;
}

interface QuantumProperties {
  dft_method: string;
  homo_energy_ev: number;
  lumo_energy_ev: number;
  bandgap_energy_ev: number;
  dipole_moment_debye: number;
  polarizability_angstrom3?: number;
  total_scf_energy_hartree: number;
  mulliken_partial_charges?: Record<string, number>;
  electrostatic_surface?: Record<string, any>;
}

interface MDSimulation {
  id: string;
  uniprot_id: string;
  system_name: string;
  organism: string;
  forcefield: string;
  solvent_model: string;
  ensemble: string;
  total_duration_ns: number;
  total_frames: number;
  timestep_ps: number;
  temperature_kelvin: number;
  pressure_bar: number;
  equilibrium_rmsd_angstrom: number;
  thermodynamic_data?: {
    potential_energy_kj_mol?: number;
    kinetic_energy_kj_mol?: number;
    total_energy_kj_mol?: number;
    density_g_cm3?: number;
  };
  trajectory_frames?: TrajectoryFrame[];
  residue_fluctuations?: ResidueFluctuation[];
  quantum_properties?: QuantumProperties;
  created_at?: string;
}

export const MolecularDynamicsPage: React.FC = () => {
  const [simulations, setSimulations] = useState<MDSimulation[]>([]);
  const [selectedSim, setSelectedSim] = useState<MDSimulation | null>(null);
  const [activeTab, setActiveTab] = useState<'trajectory' | 'rmsd' | 'rmsf' | 'quantum' | 'frames'>('trajectory');
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showSimModal, setShowSimModal] = useState<boolean>(false);

  // Trajectory Player State
  const [currentFrameIdx, setCurrentFrameIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [colorMode, setColorMode] = useState<'flexibility' | 'structure' | 'spectrum'>('flexibility');
  const [cameraAngle, setCameraAngle] = useState<number>(25);

  // Simulation Form State
  const [uniprotId, setUniprotId] = useState('Q9BYF1');
  const [systemName, setSystemName] = useState('PCSK9 Catalytic Subdomain & LNP Envelope Complex');
  const [organism, setOrganism] = useState('Homo sapiens');
  const [forcefield, setForcefield] = useState('AMBER14SB');
  const [solventModel, setSolventModel] = useState('TIP3P');
  const [ensemble, setEnsemble] = useState('NPT');
  const [durationNs, setDurationNs] = useState(100);
  const [totalFrames, setTotalFrames] = useState(30);
  const [temperatureK, setTemperatureK] = useState(300.0);
  const [pressureBar, setPressureBar] = useState(1.013);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/md/simulations');
      const data: MDSimulation[] = res.data;
      setSimulations(data);
      if (data.length > 0) {
        loadSimulationDetails(data[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load molecular dynamics simulations');
    } finally {
      setLoading(false);
    }
  };

  const loadSimulationDetails = async (id: string) => {
    try {
      const res = await api.get(`/md/simulations/${id}`);
      setSelectedSim(res.data);
      setCurrentFrameIdx(0);
      setIsPlaying(false);
    } catch (err: any) {
      console.error('Failed to load simulation detail', err);
    }
  };

  const handleRunSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSimulating(true);
      setError(null);
      const payload = {
        uniprot_id: uniprotId,
        system_name: systemName,
        organism: organism,
        forcefield: forcefield,
        solvent_model: solventModel,
        ensemble: ensemble,
        total_duration_ns: Number(durationNs),
        total_frames: Number(totalFrames),
        temperature_kelvin: Number(temperatureK),
        pressure_bar: Number(pressureBar),
      };
      const res = await api.post('/md/simulate', payload);
      await fetchSimulations();
      loadSimulationDetails(res.data.id);
      setShowSimModal(false);
      setCurrentFrameIdx(0);
    } catch (err: any) {
      setError(err.message || 'Simulation execution failed');
    } finally {
      setSimulating(false);
    }
  };

  // Trajectory playback animation loop
  useEffect(() => {
    let interval: any;
    if (isPlaying && selectedSim?.trajectory_frames && selectedSim.trajectory_frames.length > 0) {
      const frameDurationMs = Math.max(50, Math.floor(250 / playbackSpeed));
      interval = setInterval(() => {
        setCurrentFrameIdx((prev) => {
          const total = selectedSim.trajectory_frames?.length || 1;
          return (prev + 1) % total;
        });
      }, frameDurationMs);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed, selectedSim]);

  // 3D Canvas rendering for protein trajectory ribbon
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Dark molecular backdrop gradient
    const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 10, width / 2, height / 2, width / 1.5);
    bgGrad.addColorStop(0, '#0c1222');
    bgGrad.addColorStop(1, '#050811');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // Draw solvent boundary box
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.15)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.strokeRect(50, 40, width - 100, height - 80);
    ctx.setLineDash([]);

    // Water particles background simulation
    const timeSec = currentFrameIdx * 0.4;
    for (let i = 0; i < 45; i++) {
      const px = ((i * 123 + timeSec * 15) % (width - 120)) + 60;
      const py = ((i * 87 + Math.sin(timeSec + i) * 10) % (height - 100)) + 50;
      ctx.fillStyle = 'rgba(56, 189, 248, 0.2)';
      ctx.beginPath();
      ctx.arc(px, py, 1.8, 0, Math.PI * 2);
      ctx.fill();
    }

    const totalResidues = selectedSim?.residue_fluctuations?.length || 50;
    const curFrame = selectedSim?.trajectory_frames?.[currentFrameIdx];
    const rmsdFactor = curFrame ? curFrame.rmsd_angstrom : 1.45;

    // Draw 3D-projected rotating alpha-carbon backbone ribbon
    const points: { x: number; y: number; z: number; rmsf: number; ss: string; idx: number }[] = [];
    const rad = (cameraAngle * Math.PI) / 180;
    const cx = width / 2;
    const cy = height / 2;

    for (let i = 0; i < totalResidues; i++) {
      const flu = selectedSim?.residue_fluctuations?.[i];
      const rmsf = flu?.rmsf_angstrom || 1.0;
      const ss = flu?.secondary_structure_type || (i % 2 === 0 ? 'helix' : 'loop');

      // Coordinate parametric formula with dynamic fluctuation perturbation
      const t = i * 0.22;
      const wave = Math.sin(t + currentFrameIdx * 0.3) * (rmsf * 4.5);
      const xRaw = (i - totalResidues / 2) * 8.5;
      const yRaw = Math.sin(t * 1.8) * 45 + wave;
      const zRaw = Math.cos(t * 1.8) * 45 + Math.cos(currentFrameIdx * 0.2 + i) * 5;

      // 3D Rotation around Y axis
      const rotX = xRaw * Math.cos(rad) - zRaw * Math.sin(rad);
      const rotZ = xRaw * Math.sin(rad) + zRaw * Math.cos(rad);
      const rotY = yRaw;

      // Perspective projection
      const perspective = 450 / (450 + rotZ);
      const screenX = cx + rotX * perspective;
      const screenY = cy + rotY * perspective;

      points.push({ x: screenX, y: screenY, z: rotZ, rmsf, ss, idx: i });
    }

    // Sort by depth (Z) for correct rendering
    points.sort((a, b) => a.z - b.z);

    // Draw backbone ribbon connections
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    for (let i = 0; i < points.length - 1; i++) {
      const p1 = points[i];
      const p2 = points[i + 1];

      // Color coding logic
      let strokeStyle = '#38bdf8';
      if (colorMode === 'flexibility') {
        if (p1.rmsf > 1.8) strokeStyle = '#ef4444';
        else if (p1.rmsf > 1.2) strokeStyle = '#f59e0b';
        else strokeStyle = '#3b82f6';
      } else if (colorMode === 'structure') {
        if (p1.ss === 'helix') strokeStyle = '#10b981';
        else if (p1.ss === 'sheet') strokeStyle = '#f59e0b';
        else strokeStyle = '#8b5cf6';
      } else {
        const hue = (p1.idx / totalResidues) * 320;
        strokeStyle = `hsl(${hue}, 85%, 60%)`;
      }

      ctx.strokeStyle = strokeStyle;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();

      // Draw Alpha-Carbon spheres
      ctx.fillStyle = strokeStyle;
      ctx.beginPath();
      ctx.arc(p1.x, p1.y, p1.rmsf > 1.5 ? 5.5 : 4, 0, Math.PI * 2);
      ctx.fill();

      // Sphere highlight for 3D realism
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.beginPath();
      ctx.arc(p1.x - 1.5, p1.y - 1.5, 1.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // Overlay active frame watermark & telemetry
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px monospace';
    const activeNs = curFrame ? (curFrame.timestamp_ps / 1000.0).toFixed(2) : '0.00';
    ctx.fillText(`TIMESTEP: ${activeNs} ns (${curFrame?.timestamp_ps?.toFixed(1) || 0} ps)`, 65, height - 55);
    ctx.fillText(`RMSD: ${rmsdFactor.toFixed(3)} Å`, 65, height - 40);
    ctx.fillText(`FORCEFIELD: ${selectedSim?.forcefield || 'AMBER14SB'} / ${selectedSim?.solvent_model || 'TIP3P'}`, 65, height - 25);
  }, [currentFrameIdx, cameraAngle, colorMode, selectedSim]);

  const activeFrame = selectedSim?.trajectory_frames?.[currentFrameIdx];
  const dftProps = selectedSim?.quantum_properties;

  const handleExportTrajectory = () => {
    if (!selectedSim) return;
    const url = `/api/v1/md/simulations/${selectedSim.id}/export-trajectory`;
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Studio Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              Generation 13 • Phase 39 Studio
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Velocity Verlet & B3LYP DFT
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-100 flex items-center gap-3">
            <Activity className="w-8 h-8 text-cyan-400 animate-pulse" />
            Autonomous Molecular Dynamics & Quantum Chemistry
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Autonomous multi-nanosecond atomistic trajectory integration, conformational RMSD convergence profiling, per-residue RMSF flexibility loop detection, and Density Functional Theory (DFT) quantum electronic orbital synthesis.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchSimulations}
            className="p-2.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh Simulation Runs"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowSimModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-medium text-sm shadow-lg shadow-cyan-900/30 transition-all cursor-pointer"
          >
            <Zap className="w-4 h-4" />
            Run MD Simulation
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/50 border border-red-800/60 text-red-200 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Simulation Selector Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {simulations.map((sim) => (
          <div
            key={sim.id}
            onClick={() => loadSimulationDetails(sim.id)}
            className={`p-4 rounded-xl border transition-all cursor-pointer ${
              selectedSim?.id === sim.id
                ? 'bg-slate-800/90 border-cyan-500/60 shadow-lg shadow-cyan-950/40 ring-1 ring-cyan-500/30'
                : 'bg-slate-900/70 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-200 line-clamp-1">{sim.system_name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{sim.uniprot_id} • {sim.organism}</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                EQUILIBRATED
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-800/80 text-[11px]">
              <div>
                <span className="text-slate-500 block">Duration</span>
                <span className="text-slate-300 font-mono font-medium">{sim.total_duration_ns} ns</span>
              </div>
              <div>
                <span className="text-slate-500 block">Equil. RMSD</span>
                <span className="text-cyan-400 font-mono font-medium">{sim.equilibrium_rmsd_angstrom?.toFixed(2) || '1.45'} Å</span>
              </div>
              <div>
                <span className="text-slate-500 block">Forcefield</span>
                <span className="text-slate-300 font-mono truncate block">{sim.forcefield}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Studio Workstation */}
      {selectedSim ? (
        <div className="space-y-4">
          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-800 bg-slate-900/60 rounded-t-xl px-4 pt-2 gap-2 overflow-x-auto">
            <button
              onClick={() => setActiveTab('trajectory')}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 ${
                activeTab === 'trajectory'
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              3D Trajectory Time-Lapse Player
            </button>
            <button
              onClick={() => setActiveTab('rmsd')}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 ${
                activeTab === 'rmsd'
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              RMSD & Thermodynamic Equilibrium
            </button>
            <button
              onClick={() => setActiveTab('rmsf')}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 ${
                activeTab === 'rmsf'
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Gauge className="w-3.5 h-3.5" />
              Per-Residue RMSF Flexibility
            </button>
            <button
              onClick={() => setActiveTab('quantum')}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 ${
                activeTab === 'quantum'
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Atom className="w-3.5 h-3.5" />
              Quantum Chemistry & DFT Orbitals
            </button>
            <button
              onClick={() => setActiveTab('frames')}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 ${
                activeTab === 'frames'
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileCode className="w-3.5 h-3.5" />
              Snapshot Coordinates & Export
            </button>
          </div>

          {/* TAB 1: 3D Trajectory Player */}
          {activeTab === 'trajectory' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 bg-slate-900/80 border border-slate-800 rounded-b-xl p-6 shadow-xl">
              {/* Canvas Viewport (Col 1-3) */}
              <div className="lg:col-span-3 space-y-4">
                <div className="relative border border-slate-700/80 rounded-xl overflow-hidden bg-slate-950 shadow-inner">
                  <canvas ref={canvasRef} width={800} height={420} className="w-full h-[420px] block" />

                  {/* Top Canvas Badges */}
                  <div className="absolute top-4 left-4 flex gap-2">
                    <span className="px-2.5 py-1 rounded bg-slate-900/90 text-cyan-400 border border-slate-700 text-xs font-mono font-medium backdrop-blur">
                      Frame {currentFrameIdx + 1} / {selectedSim.trajectory_frames?.length || selectedSim.total_frames || 30}
                    </span>
                    <span className="px-2.5 py-1 rounded bg-slate-900/90 text-emerald-400 border border-slate-700 text-xs font-mono font-medium backdrop-blur">
                      Ensemble: {selectedSim.ensemble}
                    </span>
                  </div>

                  {/* Rotation and Camera Controls */}
                  <div className="absolute top-4 right-4 flex items-center gap-2 bg-slate-900/90 border border-slate-700 rounded-lg p-1 text-xs">
                    <button
                      onClick={() => setCameraAngle((prev) => (prev - 15 + 360) % 360)}
                      className="p-1.5 hover:bg-slate-800 text-slate-300 rounded"
                      title="Rotate Left"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                    <span className="font-mono text-slate-400 px-1">{cameraAngle}°</span>
                    <button
                      onClick={() => setCameraAngle((prev) => (prev + 15) % 360)}
                      className="p-1.5 hover:bg-slate-800 text-slate-300 rounded"
                      title="Rotate Right"
                    >
                      <RotateCcw className="w-3.5 h-3.5 transform scale-x-[-1]" />
                    </button>
                  </div>
                </div>

                {/* Player Scrubbing Bar and Playback Controls */}
                <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="p-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium shadow-md shadow-cyan-900/40 transition-colors"
                    >
                      {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </button>

                    <div className="flex items-center gap-1 bg-slate-900 border border-slate-700 rounded-lg p-1 text-xs">
                      {[0.5, 1, 2].map((spd) => (
                        <button
                          key={spd}
                          onClick={() => setPlaybackSpeed(spd)}
                          className={`px-2 py-0.5 rounded font-mono ${
                            playbackSpeed === spd
                              ? 'bg-cyan-500 text-slate-950 font-bold'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {spd}x
                        </button>
                      ))}
                    </div>

                    <div className="flex items-center gap-1 bg-slate-900 border border-slate-700 rounded-lg p-1 text-xs">
                      <button
                        onClick={() => setColorMode('flexibility')}
                        className={`px-2 py-0.5 rounded ${
                          colorMode === 'flexibility' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400'
                        }`}
                      >
                        Flexibility RMSF
                      </button>
                      <button
                        onClick={() => setColorMode('structure')}
                        className={`px-2 py-0.5 rounded ${
                          colorMode === 'structure' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400'
                        }`}
                      >
                        2° Structure
                      </button>
                    </div>
                  </div>

                  {/* Frame Scrubber Slider */}
                  <div className="flex-1 max-w-md flex items-center gap-3">
                    <span className="text-xs font-mono text-slate-400">0 ns</span>
                    <input
                      type="range"
                      min={0}
                      max={(selectedSim.trajectory_frames?.length || selectedSim.total_frames || 1) - 1}
                      value={currentFrameIdx}
                      onChange={(e) => {
                        setCurrentFrameIdx(Number(e.target.value));
                        setIsPlaying(false);
                      }}
                      className="flex-1 accent-cyan-400 bg-slate-700 h-1.5 rounded-lg cursor-pointer"
                    />
                    <span className="text-xs font-mono text-cyan-400 font-semibold">{selectedSim.total_duration_ns} ns</span>
                  </div>
                </div>
              </div>

              {/* Real-Time Telemetry Sidebar (Col 4) */}
              <div className="space-y-4">
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    Instantaneous Telemetry
                  </h4>
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center py-1 border-b border-slate-800/80">
                      <span className="text-slate-400">Simulation Time</span>
                      <span className="font-mono text-slate-200 font-medium">
                        {activeFrame ? `${(activeFrame.timestamp_ps / 1000.0).toFixed(2)} ns` : '0.00 ns'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-1 border-b border-slate-800/80">
                      <span className="text-slate-400">Backbone RMSD</span>
                      <span className="font-mono text-cyan-400 font-bold">
                        {activeFrame ? `${activeFrame.rmsd_angstrom.toFixed(3)} Å` : '--'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-1 border-b border-slate-800/80">
                      <span className="text-slate-400">Radius of Gyration</span>
                      <span className="font-mono text-slate-300">
                        {activeFrame?.radius_of_gyration_angstrom
                          ? `${activeFrame.radius_of_gyration_angstrom.toFixed(2)} Å`
                          : '--'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-1 border-b border-slate-800/80">
                      <span className="text-slate-400">Potential Energy</span>
                      <span className="font-mono text-slate-300">
                        {activeFrame?.potential_energy_kj_mol
                          ? `${activeFrame.potential_energy_kj_mol.toFixed(1)} kJ/mol`
                          : '--'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-1 border-b border-slate-800/80">
                      <span className="text-slate-400">Temperature</span>
                      <span className="font-mono text-amber-400 font-medium">
                        {activeFrame?.temperature_kelvin ? `${activeFrame.temperature_kelvin.toFixed(1)} K` : `${selectedSim.temperature_kelvin.toFixed(1)} K`}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-1">
                      <span className="text-slate-400">Pressure</span>
                      <span className="font-mono text-slate-300">{selectedSim.pressure_bar.toFixed(3)} bar</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    System Parameters
                  </h4>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between text-slate-400">
                      <span>Forcefield:</span>
                      <span className="text-slate-200 font-mono">{selectedSim.forcefield}</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Solvent:</span>
                      <span className="text-slate-200 font-mono truncate max-w-[130px]">{selectedSim.solvent_model}</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Timestep:</span>
                      <span className="text-slate-200 font-mono">{selectedSim.timestep_ps} ps</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Total Frames:</span>
                      <span className="text-slate-200 font-mono">{selectedSim.total_frames}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleExportTrajectory}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-xs font-medium transition-colors cursor-pointer"
                >
                  <Download className="w-4 h-4 text-cyan-400" />
                  Download Trajectory (.PDB)
                </button>
              </div>
            </div>
          )}

          {/* TAB 2: RMSD & Energy Convergence */}
          {activeTab === 'rmsd' && (
            <div className="space-y-6 bg-slate-900/80 border border-slate-800 rounded-b-xl p-6 shadow-xl">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                  <span className="text-xs text-slate-500 block mb-1">Equilibrium RMSD</span>
                  <span className="text-2xl font-mono font-bold text-cyan-400">
                    {selectedSim.equilibrium_rmsd_angstrom.toFixed(3)} Å
                  </span>
                  <span className="text-[11px] text-slate-400 mt-1 block">Conformational plateau</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                  <span className="text-xs text-slate-500 block mb-1">Simulation Duration</span>
                  <span className="text-2xl font-mono font-bold text-amber-400">
                    {selectedSim.total_duration_ns.toFixed(1)} ns
                  </span>
                  <span className="text-[11px] text-slate-400 mt-1 block">Atomistic time-step</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                  <span className="text-xs text-slate-500 block mb-1">Ensemble & Thermostat</span>
                  <span className="text-2xl font-mono font-bold text-emerald-400">
                    {selectedSim.ensemble}
                  </span>
                  <span className="text-[11px] text-slate-400 mt-1 block">{selectedSim.temperature_kelvin} K, {selectedSim.pressure_bar} bar</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                  <span className="text-xs text-slate-500 block mb-1">Thermodynamic Potential</span>
                  <span className="text-2xl font-mono font-bold text-indigo-400">
                    {selectedSim.thermodynamic_data?.potential_energy_kj_mol || -465000}
                  </span>
                  <span className="text-[11px] text-slate-400 mt-1 block">kJ / mol</span>
                </div>
              </div>

              {/* RMSD Convergence SVG Chart */}
              <div className="border border-slate-800 rounded-xl bg-slate-950 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">Backbone Cα RMSD Trajectory Convergence</h3>
                    <p className="text-xs text-slate-500">Root Mean Square Deviation relative to initial relaxed state</p>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="flex items-center gap-1.5 text-cyan-400">
                      <span className="w-3 h-0.5 bg-cyan-400 inline-block" /> RMSD Profile
                    </span>
                    <span className="flex items-center gap-1.5 text-emerald-400">
                      <span className="w-3 h-0.5 bg-emerald-400 border-dashed border-t inline-block" /> Equilibrium Plateau
                    </span>
                  </div>
                </div>

                <div className="h-64 w-full">
                  <svg className="w-full h-full" viewBox="0 0 700 200" preserveAspectRatio="none">
                    {/* Grid lines */}
                    <line x1="40" y1="20" x2="680" y2="20" stroke="#1e293b" strokeDasharray="3 3" />
                    <line x1="40" y1="60" x2="680" y2="60" stroke="#1e293b" strokeDasharray="3 3" />
                    <line x1="40" y1="100" x2="680" y2="100" stroke="#1e293b" strokeDasharray="3 3" />
                    <line x1="40" y1="140" x2="680" y2="140" stroke="#1e293b" strokeDasharray="3 3" />
                    <line x1="40" y1="180" x2="680" y2="180" stroke="#334155" />

                    {/* Y Axis Labels */}
                    <text x="30" y="25" fill="#64748b" fontSize="9" textAnchor="end">2.5 Å</text>
                    <text x="30" y="85" fill="#64748b" fontSize="9" textAnchor="end">1.5 Å</text>
                    <text x="30" y="145" fill="#64748b" fontSize="9" textAnchor="end">0.5 Å</text>
                    <text x="30" y="185" fill="#64748b" fontSize="9" textAnchor="end">0.0 Å</text>

                    {/* Equilibrium Reference Line */}
                    <line x1="40" y1="85" x2="680" y2="85" stroke="#10b981" strokeWidth="1.5" strokeDasharray="4 4" />

                    {/* RMSD Data Curve */}
                    {selectedSim.trajectory_frames && selectedSim.trajectory_frames.length > 1 && (
                      <polyline
                        fill="none"
                        stroke="#38bdf8"
                        strokeWidth="2.5"
                        points={selectedSim.trajectory_frames
                          .map((f, i) => {
                            const x = 40 + (i / (selectedSim.trajectory_frames!.length - 1)) * 640;
                            const y = 180 - (Math.min(2.5, f.rmsd_angstrom) / 2.5) * 160;
                            return `${x},${y}`;
                          })
                          .join(' ')}
                      />
                    )}
                  </svg>
                </div>
                <div className="flex justify-between text-xs text-slate-500 mt-2 px-10">
                  <span>0 ns (Relaxation Start)</span>
                  <span>{(selectedSim.total_duration_ns / 2).toFixed(1)} ns</span>
                  <span>{selectedSim.total_duration_ns} ns (Equilibrated Production)</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Per-Residue RMSF Flexibility */}
          {activeTab === 'rmsf' && (
            <div className="space-y-6 bg-slate-900/80 border border-slate-800 rounded-b-xl p-6 shadow-xl">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-200">Per-Residue Root Mean Square Fluctuation (RMSF)</h3>
                  <p className="text-xs text-slate-500">Atomic flexibility mapping & catalytic loop identification</p>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="flex items-center gap-1.5 text-red-400">
                    <span className="w-2.5 h-2.5 bg-red-500 rounded-sm" /> Flexible Loops (&gt; 1.5 Å)
                  </span>
                  <span className="flex items-center gap-1.5 text-blue-400">
                    <span className="w-2.5 h-2.5 bg-blue-500 rounded-sm" /> Rigid Helices (&lt; 1.0 Å)
                  </span>
                </div>
              </div>

              {/* RMSF Bar Chart */}
              <div className="border border-slate-800 rounded-xl bg-slate-950 p-6">
                <div className="h-64 w-full flex items-end gap-1.5 px-2">
                  {selectedSim.residue_fluctuations?.map((rf) => {
                    const heightPct = Math.min(100, (rf.rmsf_angstrom / 3.0) * 100);
                    const isHigh = rf.is_flexible_loop || rf.rmsf_angstrom > 1.5;
                    const isRigid = rf.rmsf_angstrom < 1.0;

                    return (
                      <div
                        key={rf.id}
                        className="flex-1 flex flex-col items-center group relative cursor-pointer"
                        title={`${rf.residue_name} ${rf.residue_number}: ${rf.rmsf_angstrom.toFixed(2)} Å (${rf.secondary_structure_type})`}
                      >
                        <div
                          style={{ height: `${heightPct}%` }}
                          className={`w-full rounded-t-sm transition-all duration-300 group-hover:brightness-125 ${
                            isHigh ? 'bg-red-500 shadow-sm shadow-red-500/50' : isRigid ? 'bg-blue-600' : 'bg-amber-500'
                          }`}
                        />
                      </div>
                    );
                  })}
                </div>
                <div className="flex justify-between text-xs text-slate-500 mt-3 px-2 border-t border-slate-800 pt-2">
                  <span>Residue 1 (N-Terminus)</span>
                  <span>Residue {Math.floor((selectedSim.residue_fluctuations?.length || 50) / 2)}</span>
                  <span>Residue {selectedSim.residue_fluctuations?.length || 50} (C-Terminus)</span>
                </div>
              </div>

              {/* Identified Dynamic Regions Table */}
              <div className="border border-slate-800 rounded-xl bg-slate-950 overflow-hidden">
                <div className="p-4 border-b border-slate-800 bg-slate-900/50">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Identified Conformational Dynamic Loops & Hinge Regions
                  </h4>
                </div>
                <div className="divide-y divide-slate-800/80 max-h-60 overflow-y-auto">
                  {selectedSim.residue_fluctuations
                    ?.filter((r) => r.is_flexible_loop)
                    .map((r) => (
                      <div key={r.id} className="p-3 px-4 flex items-center justify-between text-xs hover:bg-slate-900/40">
                        <div className="flex items-center gap-3">
                          <span className="font-mono font-bold text-slate-200">
                            {r.residue_name} {r.residue_number}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 font-mono">
                            {r.secondary_structure_type}
                          </span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="font-mono text-cyan-400 font-bold">{r.rmsf_angstrom.toFixed(3)} Å</span>
                          <span className="px-2 py-0.5 rounded text-[10px] bg-red-950/80 text-red-400 border border-red-800/50 font-medium">
                            Flexible Loop
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: Quantum Chemistry & DFT Orbitals */}
          {activeTab === 'quantum' && (
            <div className="space-y-6 bg-slate-900/80 border border-slate-800 rounded-b-xl p-6 shadow-xl">
              {dftProps ? (
                <div className="space-y-6">
                  {/* High Level Electronic Properties Banner */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-xs text-slate-500 block mb-1">HOMO-LUMO Bandgap (ΔE)</span>
                      <span className="text-2xl font-mono font-bold text-cyan-400">
                        {dftProps.bandgap_energy_ev.toFixed(2)} eV
                      </span>
                      <span className="text-[11px] text-slate-400 mt-1 block">Electronic excitation energy</span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-xs text-slate-500 block mb-1">Dipole Moment (μ)</span>
                      <span className="text-2xl font-mono font-bold text-amber-400">
                        {dftProps.dipole_moment_debye.toFixed(2)} Debye
                      </span>
                      <span className="text-[11px] text-slate-400 mt-1 block">Molecular polarity</span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-xs text-slate-500 block mb-1">Total SCF Energy</span>
                      <span className="text-2xl font-mono font-bold text-indigo-400 truncate block">
                        {dftProps.total_scf_energy_hartree.toFixed(3)}
                      </span>
                      <span className="text-[11px] text-slate-400 mt-1 block">Hartrees (a.u.)</span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-xs text-slate-500 block mb-1">Method & Basis Set</span>
                      <span className="text-lg font-mono font-bold text-emerald-400 block truncate">
                        {dftProps.dft_method}
                      </span>
                      <span className="text-[11px] text-slate-400 mt-1 block">DFT Functional</span>
                    </div>
                  </div>

                  {/* Frontier Molecular Orbital Diagram */}
                  <div className="border border-slate-800 rounded-xl bg-slate-950 p-6">
                    <h3 className="text-sm font-semibold text-slate-200 mb-2">
                      Frontier Molecular Orbital Energy Diagram
                    </h3>
                    <p className="text-xs text-slate-500 mb-6">
                      Highest Occupied (HOMO) and Lowest Unoccupied (LUMO) molecular electronic orbitals
                    </p>

                    <div className="max-w-md mx-auto space-y-4 py-4">
                      {/* LUMO Level */}
                      <div className="p-3 bg-red-950/40 border border-red-700/60 rounded-lg flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="w-3 h-3 rounded-full bg-red-500" />
                          <div>
                            <span className="text-xs font-bold text-red-300 block">LUMO Level</span>
                            <span className="text-[10px] text-slate-400">Lowest Unoccupied Orbital</span>
                          </div>
                        </div>
                        <span className="text-sm font-mono font-bold text-red-300">
                          {dftProps.lumo_energy_ev.toFixed(2)} eV
                        </span>
                      </div>

                      {/* Bandgap Indicator */}
                      <div className="flex items-center justify-center gap-2 py-2 text-xs text-cyan-400 font-mono">
                        <div className="h-8 border-l-2 border-dashed border-cyan-500/50" />
                        <span>ΔE = {dftProps.bandgap_energy_ev.toFixed(2)} eV</span>
                        <div className="h-8 border-l-2 border-dashed border-cyan-500/50" />
                      </div>

                      {/* HOMO Level */}
                      <div className="p-3 bg-blue-950/40 border border-blue-700/60 rounded-lg flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="w-3 h-3 rounded-full bg-blue-500" />
                          <div>
                            <span className="text-xs font-bold text-blue-300 block">HOMO Level</span>
                            <span className="text-[10px] text-slate-400">Highest Occupied Orbital</span>
                          </div>
                        </div>
                        <span className="text-sm font-mono font-bold text-blue-300">
                          {dftProps.homo_energy_ev.toFixed(2)} eV
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 text-sm">
                  No Quantum Chemistry / DFT calculation recorded for this simulation run.
                </div>
              )}
            </div>
          )}

          {/* TAB 5: Snapshot Coordinates & Export */}
          {activeTab === 'frames' && (
            <div className="space-y-4 bg-slate-900/80 border border-slate-800 rounded-b-xl p-6 shadow-xl">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-200">Trajectory Frame Snapshots</h3>
                  <p className="text-xs text-slate-500">Atomic coordinate trajectory checkpoints</p>
                </div>
                <button
                  onClick={handleExportTrajectory}
                  className="flex items-center gap-2 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold transition-colors cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  Export Multi-Model PDB
                </button>
              </div>

              <div className="border border-slate-800 rounded-xl bg-slate-950 overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="p-3 px-4">Frame Index</th>
                      <th className="p-3 px-4">Time (ps)</th>
                      <th className="p-3 px-4">RMSD (Å)</th>
                      <th className="p-3 px-4">Radius of Gyration (Å)</th>
                      <th className="p-3 px-4">Potential Energy</th>
                      <th className="p-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80 font-mono text-slate-300">
                    {selectedSim.trajectory_frames?.map((frame, idx) => (
                      <tr
                        key={frame.id}
                        className={`hover:bg-slate-900/50 cursor-pointer ${
                          idx === currentFrameIdx ? 'bg-cyan-950/30 text-cyan-300' : ''
                        }`}
                        onClick={() => {
                          setCurrentFrameIdx(idx);
                          setActiveTab('trajectory');
                        }}
                      >
                        <td className="p-3 px-4 font-bold">#{frame.frame_index}</td>
                        <td className="p-3 px-4">{frame.timestamp_ps.toFixed(1)} ps</td>
                        <td className="p-3 px-4 text-cyan-400 font-bold">{frame.rmsd_angstrom.toFixed(3)} Å</td>
                        <td className="p-3 px-4">{frame.radius_of_gyration_angstrom.toFixed(2)} Å</td>
                        <td className="p-3 px-4">
                          {frame.potential_energy_kj_mol ? `${frame.potential_energy_kj_mol.toFixed(1)} kJ/mol` : '--'}
                        </td>
                        <td className="p-3 px-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setCurrentFrameIdx(idx);
                              setActiveTab('trajectory');
                            }}
                            className="text-xs text-cyan-400 hover:underline cursor-pointer"
                          >
                            View 3D
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : loading ? (
        <div className="text-center py-20 text-slate-400">Loading Molecular Dynamics & Quantum Studio...</div>
      ) : (
        <div className="text-center py-20 text-slate-400">No simulations found. Run a new MD simulation to begin!</div>
      )}

      {/* New Simulation Modal */}
      {showSimModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Zap className="w-5 h-5 text-cyan-400" />
                Configure Atomistic MD & Quantum Simulation
              </h2>
              <button
                onClick={() => setShowSimModal(false)}
                className="text-slate-400 hover:text-slate-200 text-sm font-mono"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleRunSimulation} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Target System Name</label>
                <input
                  type="text"
                  value={systemName}
                  onChange={(e) => setSystemName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-slate-400 block mb-1">UniProt ID</label>
                  <input
                    type="text"
                    value={uniprotId}
                    onChange={(e) => setUniprotId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Organism</label>
                  <input
                    type="text"
                    value={organism}
                    onChange={(e) => setOrganism(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Forcefield</label>
                  <select
                    value={forcefield}
                    onChange={(e) => setForcefield(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono"
                  >
                    <option value="AMBER14SB">AMBER14SB</option>
                    <option value="CHARMM36m">CHARMM36m</option>
                    <option value="OPLS_AA">OPLS-AA</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Solvent Model</label>
                  <select
                    value={solventModel}
                    onChange={(e) => setSolventModel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  >
                    <option value="TIP3P">TIP3P Explicit</option>
                    <option value="OPC">OPC 4-Point</option>
                    <option value="implicit_GB">Implicit GB-OBC</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Ensemble</label>
                  <select
                    value={ensemble}
                    onChange={(e) => setEnsemble(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono"
                  >
                    <option value="NPT">NPT (Isobaric)</option>
                    <option value="NVT">NVT (Canonical)</option>
                    <option value="NVE">NVE (Microcanonical)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Duration (ns)</label>
                  <input
                    type="number"
                    value={durationNs}
                    onChange={(e) => setDurationNs(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Frames</label>
                  <input
                    type="number"
                    value={totalFrames}
                    onChange={(e) => setTotalFrames(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Temp (K)</label>
                  <input
                    type="number"
                    value={temperatureK}
                    onChange={(e) => setTemperatureK(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Pressure (bar)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={pressureBar}
                    onChange={(e) => setPressureBar(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowSimModal(false)}
                  className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={simulating}
                  className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-medium shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50 cursor-pointer"
                >
                  {simulating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                  {simulating ? 'Synthesizing Trajectory...' : 'Run Simulation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default MolecularDynamicsPage;
