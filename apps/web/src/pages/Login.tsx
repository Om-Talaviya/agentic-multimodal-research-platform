import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { api } from '../services/api'

export function Login() {
  const [loginError, setLoginError] = useState<string | null>(null)
  const [loggingIn, setLoggingIn] = useState(false)
  const [success, setSuccess] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const search = new URLSearchParams(location.search)
  const from = search.get('from') || '/dashboard'

  useEffect(() => {
    // If already authenticated, redirect to intended destination
    const token = localStorage.getItem('token')
    if (token) {
      setSuccess(true)
    }
  }, [location, search])

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoggingIn(true)
    setLoginError(null)
    setSuccess(false)

    try {
      const formData = new FormData(e.currentTarget)
      const username = formData.get('username') as string
      const password = formData.get('password') as string

      const response = await api.post('/auth/login', {
        username,
        password,
      })

      const { access_token, refresh_token } = response.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Navigate to intended destination
      setSuccess(true)
      setTimeout(() => {
        navigate(from, { replace: true })
      }, 100)
    } catch (err: any) {
      setLoginError(err.response?.data?.error || 'Login failed')
      setLoggingIn(false)
    }
  }

  if (success) {
    return <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
      <Loader2 className="loading-spinner" size={32} />
    </div>
  }

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', marginBottom: 'var(--spacing-lg)' }}>
        Sign In
      </h1>

      {loginError && (
        <div style={{
          padding: 'var(--spacing-md)',
          background: '#fee2e2',
          color: '#991b1b',
          borderRadius: 'var(--radius-md)',
          marginBottom: 'var(--spacing-md)',
        }}>
          {loginError}
        </div>
      )}

      <form onSubmit={handleLogin} style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
        <div>
          <label className="label">Username or Email</label>
          <input
            type="text"
            name="username"
            className="input"
            placeholder="username or email"
            required
          />
        </div>

        <div>
          <label className="label">Password</label>
          <input
            type="password"
            name="password"
            className="input"
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loggingIn}
          className="btn btn-primary"
        >
          {loggingIn ? (
            <> <Loader2 size={18} /> Signing in </>
          ) : (
            <> Sign in </>
          )}
        </button>
      </form>

      <p style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)', color: 'var(--color-text-muted)' }}>
        Don't have an account? <a href="/register">Register here</a>
      </p>
    </div>
  )
}