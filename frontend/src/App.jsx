import { useEffect, useState } from 'react'
import { getHealth } from './api.js'

function App() {
  // { phase: 'loading' } | { phase: 'ready', groqConfigured } | { phase: 'error', message }
  const [state, setState] = useState({ phase: 'loading' })

  useEffect(() => {
    let ignore = false
    getHealth()
      .then((health) => {
        if (!ignore) setState({ phase: 'ready', groqConfigured: health.groq_configured })
      })
      .catch((err) => {
        if (!ignore) setState({ phase: 'error', message: err.message })
      })
    return () => {
      ignore = true
    }
  }, [])

  return (
    <main>
      <h1>PDF Chatbot</h1>
      {state.phase === 'loading' && (
        <section className="status loading" role="status">
          <h2>Checking backend…</h2>
        </section>
      )}
      {state.phase === 'ready' && state.groqConfigured && (
        <section className="status connected" role="status">
          <h2>Backend connected</h2>
          <p>Groq API key: configured.</p>
        </section>
      )}
      {state.phase === 'ready' && !state.groqConfigured && (
        <section className="status warning" role="status">
          <h2>Backend connected</h2>
          <p>
            Groq API key is not configured. Add <code>GROQ_API_KEY</code> to{' '}
            <code>backend/.env</code> and restart the backend.
          </p>
        </section>
      )}
      {state.phase === 'error' && (
        <section className="status error" role="alert">
          <h2>Backend unreachable</h2>
          <p>{state.message}</p>
          <p>Start the backend (see the README) and reload this page.</p>
        </section>
      )}
    </main>
  )
}

export default App
