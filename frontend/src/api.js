// The only module that talks to the backend.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
const TIMEOUT_MS = 5000

/**
 * Ask the backend for its health.
 * Resolves with { status: 'ok', groq_configured: boolean }.
 * Rejects with an Error whose message is safe to show to the user when the
 * backend is down, slow (> 5 s), returns a non-2xx status, or sends a
 * malformed body.
 */
export async function getHealth() {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)
  try {
    const response = await fetch(`${BASE_URL}/api/health`, { signal: controller.signal })
    if (!response.ok) {
      throw new Error(`The backend answered with HTTP ${response.status}.`)
    }
    let data
    try {
      data = await response.json()
    } catch (err) {
      if (err.name === 'AbortError') throw err
      throw new Error('The backend sent a response that is not valid JSON.')
    }
    if (data?.status !== 'ok' || typeof data.groq_configured !== 'boolean') {
      throw new Error('The backend sent an unexpected health response.')
    }
    return data
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('The backend did not respond within 5 seconds.')
    }
    if (err instanceof TypeError) {
      // fetch() rejects with TypeError for network failures (refused, CORS, DNS).
      throw new Error(`Could not reach the backend at ${BASE_URL}.`)
    }
    throw err
  } finally {
    clearTimeout(timer)
  }
}
