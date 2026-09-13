import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { NewResearch } from './pages/NewResearch'
import { ResearchDetail } from './pages/ResearchDetail'
import { Settings } from './pages/Settings'
import { MemoryPage } from './pages/MemoryPage'
import { KnowledgeGraphPage } from './pages/KnowledgeGraphPage'
import { ProjectsPage } from './pages/ProjectsPage'
import { ModelEvaluationPage } from './pages/ModelEvaluationPage'
import { AgentEvaluationPage } from './pages/AgentEvaluationPage'
import { EnterpriseSecurityPage } from './pages/EnterpriseSecurityPage'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { WorkspaceProvider } from './context/WorkspaceContext'
import { Loader2 } from 'lucide-react'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [refreshInProgress, setRefreshInProgress] = useState(false)

  useEffect(() => {
    // Check authentication on mount by reading token from localStorage
    const token = localStorage.getItem('token')
    const refreshToken = localStorage.getItem('refresh_token')

    if (token) {
      // Validate the token by calling /auth/me
      import('./services/api').then(({ api }) => {
        api.get('/auth/me').then(() => {
          setIsAuthenticated(true)
        }).catch(async (_err: unknown) => {
          // Token invalid/expired, try refresh
          if (!refreshInProgress && refreshToken) {
            setRefreshInProgress(true)
            try {
              const resp = await api.post('/auth/token/refresh', {
                refresh_token: refreshToken,
              })
              const { access_token, refresh_token: newRefreshToken } = resp.data
              localStorage.setItem('token', access_token)
              localStorage.setItem('refresh_token', newRefreshToken)
              setIsAuthenticated(true)
            } catch (refreshErr) {
              // Refresh failed, clear auth and redirect to login
              localStorage.removeItem('token')
              localStorage.removeItem('refresh_token')
              setIsAuthenticated(false)
            } finally {
              setRefreshInProgress(false)
            }
          } else {
            // No refresh token or already refreshing, clear auth
            localStorage.removeItem('token')
            localStorage.removeItem('refresh_token')
            setIsAuthenticated(false)
          }
        })
      })
    } else {
      setIsAuthenticated(false)
    }
    setIsLoading(false)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    setIsAuthenticated(false)
  }

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
        <Loader2 className="loading-spinner" size={32} />
      </div>
    )
  }

  const authenticatedRoutes = (
    <WorkspaceProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="research/new" element={<NewResearch />} />
          <Route path="research/:id" element={<ResearchDetail />} />
          <Route path="memory" element={<MemoryPage />} />
          <Route path="graph" element={<KnowledgeGraphPage />} />
          <Route path="evaluations" element={<ModelEvaluationPage />} />
          <Route path="agents/evaluations" element={<AgentEvaluationPage />} />
          <Route path="security" element={<EnterpriseSecurityPage />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Fallbacks & Auth Redirects */}
        <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        <Route path="/register" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/logout"
          element={
            <>
              {handleLogout()}
              <Navigate to="/login" replace />
            </>
          }
        />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </WorkspaceProvider>
  )

  const unauthenticatedRoutes = (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )

  return isAuthenticated ? authenticatedRoutes : unauthenticatedRoutes
}

export default App