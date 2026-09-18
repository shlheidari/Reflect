const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

// The access token lives only in memory — never localStorage/sessionStorage —
// so it can't be read by anything that persists across a page reload. The
// refresh token never reaches JS at all: it travels as an httpOnly cookie
// (see backend/apps/accounts/views.py), set with `credentials: 'include'`.
let accessToken: string | null = null

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export class ApiError extends Error {
  status: number
  code: string

  constructor(status: number, detail: string, code: string) {
    super(detail)
    this.status = status
    this.code = code
  }
}

async function parseError(response: Response): Promise<ApiError> {
  try {
    const data = await response.json()
    return new ApiError(response.status, data.detail ?? 'خطایی رخ داد.', data.code ?? 'error')
  } catch {
    return new ApiError(response.status, 'خطایی رخ داد.', 'error')
  }
}

// De-dupes concurrent refresh attempts (e.g. two components hitting a 401 at
// once, or React StrictMode's double effect invocation in dev) into a single
// network request, so a rotating refresh token never gets used twice.
let refreshPromise: Promise<string | null> | null = null

export function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE_URL}/auth/refresh/`, {
      method: 'POST',
      credentials: 'include',
    })
      .then(async (response) => {
        if (!response.ok) return null
        const data = await response.json()
        return data.access as string
      })
      .catch(() => null)
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

interface ApiRequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  /** Skip the automatic refresh-and-retry-once on 401 (used by auth endpoints themselves). */
  skipAuthRetry?: boolean
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { body, skipAuthRetry, headers, ...rest } = options
  // `path` is sometimes a full URL rather than an API-relative one — DRF's
  // paginator hands back absolute `next` links (see fetchAllPages below).
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`

  const doFetch = () =>
    fetch(url, {
      ...rest,
      credentials: 'include',
      headers: {
        ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })

  let response = await doFetch()

  if (response.status === 401 && !skipAuthRetry) {
    const newToken = await refreshAccessToken()
    if (newToken) {
      accessToken = newToken
      response = await doFetch()
    }
  }

  if (!response.ok) {
    throw await parseError(response)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

interface PaginatedPage<T> {
  next: string | null
  results: T[]
}

// DRF paginates every list endpoint at PAGE_SIZE=20 by default (see
// backend/config/settings.py). Several list pages here were only reading
// `.results` off the first page, so an event with more than 20 participants
// silently hid everyone past page 1 — this walks `next` until it's exhausted.
export async function fetchAllPages<T>(path: string): Promise<T[]> {
  const items: T[] = []
  let next: string | null = path
  while (next) {
    const page: PaginatedPage<T> = await apiRequest<PaginatedPage<T>>(next)
    items.push(...page.results)
    next = page.next
  }
  return items
}
