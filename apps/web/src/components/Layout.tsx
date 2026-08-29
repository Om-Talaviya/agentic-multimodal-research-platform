import { NavLink, Outlet } from 'react-router-dom'
import { LayoutDashboard, Plus, Settings, FlaskConical } from 'lucide-react'

export function Layout() {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/research/new', label: 'New Research', icon: Plus },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside style={{
        width: '260px',
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
          marginBottom: 'var(--spacing-xl)',
          fontSize: '1.25rem',
          fontWeight: 600,
          color: 'var(--color-primary)',
        }}>
          <FlaskConical size={28} />
          <span>Research Platform</span>
        </div>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
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
              })}
            >
              <item.icon size={20} />
              {item.label}
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