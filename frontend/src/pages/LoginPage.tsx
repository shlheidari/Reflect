import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/authContext'

export function LoginPage() {
  const { login, status } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  if (status === 'authenticated') {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setErrorMessage(null)
    try {
      await login(username, password)
      navigate('/', { replace: true })
    } catch {
      setErrorMessage('نام کاربری یا رمز عبور اشتباه است.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-fuchsia-50 via-white to-violet-50 p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-3xl bg-white p-8 shadow-xl shadow-fuchsia-900/5"
      >
        <div className="text-center">
          <span className="text-5xl">🪞</span>
          <h1 className="mt-3 text-xl font-bold text-gray-900">آینه</h1>
          <p className="mt-1 text-sm text-gray-500">با نام کاربری‌ای که از مدیر گرفتی وارد شو</p>
        </div>

        <label className="mb-1 mt-6 block text-sm text-gray-700" htmlFor="username">
          نام کاربری
        </label>
        <input
          id="username"
          className="mb-4 w-full rounded-xl border border-gray-300 px-3 py-2.5 transition-colors focus:border-fuchsia-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/30"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          required
        />

        <label className="mb-1 block text-sm text-gray-700" htmlFor="password">
          رمز عبور
        </label>
        <input
          id="password"
          type="password"
          className="mb-4 w-full rounded-xl border border-gray-300 px-3 py-2.5 transition-colors focus:border-fuchsia-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/30"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />

        {errorMessage && (
          <p className="mb-4 text-sm text-red-600" role="alert">
            {errorMessage}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-xl bg-gradient-to-l from-fuchsia-600 to-violet-600 py-3 font-medium text-white transition-opacity focus:outline-none focus:ring-2 focus:ring-fuchsia-500/40 focus:ring-offset-2 disabled:opacity-50"
        >
          {submitting ? 'در حال ورود...' : 'ورود'}
        </button>
      </form>
    </div>
  )
}
