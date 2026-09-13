import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { api } from '../services/api'

export function Register() {
  const [registerError, setRegisterError] = useState<string | null>(null)
  const [registering, setRegistering] = useState(false)
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    // If registration successful and already authenticated, redirect to dashboard
    // If registering for the first time, redirect to login page
    const token = localStorage.getItem('token')
    if (token) {
      // User is now authenticated via registration
      setTimeout(() => {
        navigate('/dashboard', { replace: true })
      }, 100)
    } else {
      // No token yet - redirect to login (shouldn't happen if registration works)
      navigate('/login', { replace: true })
    }
  }, [navigate])

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setRegistering(true)
    setRegisterError(null)
    setSuccess(false)

    try {
      const formData = new FormData(e.currentTarget)
      const username = formData.get('username') as string
      const password = formData.get('password') as string

      const response = await api.post('/auth/register', {
        username,
        password,
      })

      const { access_token, refresh_token } = response.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      setSuccess(true)
    } catch (err: any) {
      setRegisterError(err.response?.data?.error || 'Registration failed')
      setRegistering(false)
    }
  }

  if (success) {
    // Effect will handle navigation
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
        <Loader2 className="loading-spinner" size={32} />
      </div>
    )
  }

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', marginBottom: 'var(--spacing-lg)' }}>
        Sign Up
      </h1>

      {registerError && (
        <div style={{
          padding: 'var(--spacing-md)',
          background: '#fee2e2',
          color: '#991b1b',
          borderRadius: 'var(--radius-md)',
          marginBottom: 'var(--spacing-md)',
        }}>
          {registerError}
        </div>
      )}

      <form onSubmit={handleRegister} style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
        <div>
          <label className="label">Username</label>
          <input
            type="text"
            name="username"
            className="input"
            placeholder="username"
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
          disabled={registering}
          className="btn btn-primary"
        >
          {registering ? (
            <> <Loader2 size={18} /> Creating account </>
          ) : (
            <> Create account </>
          )}
        </button>
      </form>

      <p style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)', color: 'var(--color-text-muted)' }}>
        Already have an account? <a href="/login">Sign in here</a>
      </p>
    </div>
  )
}