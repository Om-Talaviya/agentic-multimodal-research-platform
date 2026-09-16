import { NavLink, Outlet } from 'react-router-dom'
import {
  Flame,
  LayoutDashboard, Plus, Settings, FlaskConical, Brain, Share2,
  FolderKanban, Trophy, Activity, ShieldCheck, Server, Code2,
  Radio, Swords, BookOpenCheck, Cpu, Presentation, Award,
  Network, Database, Scale, FileSpreadsheet, HeartPulse, Bot,
  Dna, Atom, Scissors, Microscope, Layers, Pill
} from 'lucide-react'
import { WorkspaceSelector } from './WorkspaceSelector'

export function Layout() {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/projects', label: 'Projects', icon: FolderKanban },
    { path: '/research/new', label: 'New Research', icon: Plus },
    { path: '/spatial', label: 'Spatial Multi-Omics', icon: Layers },
    { path: '/single-cell', label: 'Single-Cell Transcriptomics', icon: Microscope },
    { path: '/chemistry', label: 'Generative Therapeutics', icon: FlaskConical },
    { path: '/supergraph', label: 'Knowledge Super-Graph', icon: Network },
    { path: '/synergy', label: 'Drug Synergy & Repurposing', icon: Pill },
    { path: '/crispr', label: 'CRISPR & Synthetic Bio', icon: Scissors },
    { path: '/molecular', label: 'Bio-Molecular Structure', icon: Dna },
    { path: '/dynamics', label: 'MD Trajectory & Quantum', icon: Atom },
    { path: '/canvas', label: 'Research Canvas', icon: Network },
    { path: '/datasets', label: 'Dataset Synthesis', icon: Database },
    { path: '/patents', label: 'Patent Landscape', icon: Scale },
    { path: '/grants', label: 'Grant Proposals', icon: FileSpreadsheet },
    { path: '/clinical', label: 'Clinical Trials & Repurposing', icon: HeartPulse },
    { path: '/lab', label: 'Robotic Lab Automation', icon: Bot },
    { path: '/debates', label: 'Debate Arena', icon: Swords },
    { path: '/literature', label: 'Literature Reviews', icon: BookOpenCheck },
    { path: '/reproducibility', label: 'In-Silico Verification', icon: Cpu },
    { path: '/presentations', label: 'Briefing Studio', icon: Presentation },
    { path: '/publishing', label: 'Peer Review & Publishing', icon: Award },
    { path: '/memory', label: 'Memory', icon: Brain },
    { path: '/graph', label: 'Knowledge Graph', icon: Share2 },
    { path: '/evaluations', label: 'Model Benchmarks', icon: Trophy },
    { path: '/agents/evaluations', label: 'Agent Observability', icon: Activity },
    { path: '/ragas-eval', label: 'RAGAS & Red-Teaming', icon: ShieldCheck },
    { path: '/lakehouse', label: 'Multimodal Lakehouse', icon: Database },
    { path: '/eln', label: 'Electronic Lab Notebook', icon: BookOpenCheck },
    { path: '/vhts', label: 'Virtual HTS & Docking', icon: Flame },
    { path: '/security', label: 'Enterprise Security', icon: ShieldCheck },
    { path: '/infrastructure', label: 'Infrastructure', icon: Server },
    { path: '/developer', label: 'Developer API', icon: Code2 },
    { path: '/automation', label: 'Research Automation', icon: Radio },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside style={{
        width: '280px',
        background: 'var(--color-surface)',
        borderRight: '1px solid var(--color-border)',
        padding: 'var(--spacing-lg)',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-sm)',
          marginBottom: 'var(--spacing-lg)',
          fontSize: '1.25rem',
          fontWeight: 600,
          color: 'var(--color-primary)',
        }}>
          <FlaskConical size={28} />
          <span>Research Platform</span>
        </div>

        {/* Workspace & Project Selector */}
        <WorkspaceSelector />
        
        <nav style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-xs)',
          overflowY: 'auto',
          maxHeight: 'calc(100vh - 180px)',
          paddingRight: '4px'
        }}>
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                padding: 'var(--spacing-sm) var(--spacing-md)',
                borderRadius: 'var(--radius-md)',
                color: isActive ? 'var(--color-primary)' : 'var(--color-text)',
                background: isActive ? 'var(--color-primary)' + '15' : 'transparent',
                textDecoration: 'none',
                fontWeight: isActive ? 600 : 400,
                transition: 'all 0.2s',
                fontSize: '0.875rem'
              })}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      
      <main style={{ flex: 1, padding: 'var(--spacing-xl)', overflow: 'auto' }}>
        <Outlet />
      </main>
    </div>
  )
}

