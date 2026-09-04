import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { NewResearch } from './pages/NewResearch'
import { ResearchDetail } from './pages/ResearchDetail'
import { Settings } from './pages/Settings'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
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

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {isAuthenticated ? (
          <Route index element={<Navigate to="/dashboard" replace />} />
        ) : (
          <Route index element={<Navigate to="/login" replace />} />
        )}
      </Route>

      <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />} />
      <Route path="research/new" element={isAuthenticated ? <NewResearch /> : <Navigate to="/login" replace />} />
      <Route path="research/:id" element={isAuthenticated ? <ResearchDetail /> : <Navigate to="/login" replace />} />
      <Route path="settings" element={isAuthenticated ? <Settings /> : <Navigate to="/login" replace />} />

      {/* Auth routes - only when not authenticated */}
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" replace />} />
      <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/login" replace />} />

      {/* Protected auth routes with logout */}
      <Route
        path="/logout"
        element={isAuthenticated ? (
          <>
            {handleLogout()}
            <Navigate to="/login" replace />
          </>
        ) : (
          <Navigate to="/login" replace />
        )}
      />

      {/* Expiration warning */}
      <Route path="/token-expired" element={!isAuthenticated ? <Login /> : <Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App