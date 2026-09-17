import { useState } from 'react'
import { Radio, Activity } from 'lucide-react'

export default function App() {
  const [status, setStatus] = useState('Connection not checked')
  const [busy, setBusy] = useState(false)

  async function checkBackend() {
    setBusy(true)
    setStatus('Checking...')
    try {
      const response = await fetch('/api/health/')
      if (!response.ok) throw new Error('API unavailable')
      const data = await response.json()
      if (data.status !== 'ok') throw new Error('Unexpected response')
      setStatus('Connected to NetSage API')
    } catch {
      setStatus('Cannot connect. Start Django on port 8000, then retry.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8">
      <header className="flex items-center gap-3 text-xl font-bold">
        <Radio className="text-blue-600" aria-hidden="true" />
        NetSage
      </header>
      <section className="my-auto max-w-3xl py-20">
        <p className="mb-5 text-sm font-semibold uppercase tracking-widest text-blue-600">
          Network monitoring and incident response
        </p>
        <h1 className="text-5xl font-extrabold leading-tight tracking-tight sm:text-7xl">
          Network clarity.
          <span className="block text-red-600">Connected communities.</span>
        </h1>
        <p className="mt-7 max-w-xl text-lg leading-8 text-slate-600">
          Spot service problems, investigate related alerts, coordinate
          engineers, and keep customers informed.
        </p>
        <div className="mt-10 rounded-2xl border border-slate-200 bg-white p-6">
          <h2 className="flex items-center gap-2 font-semibold">
            <Activity className="text-blue-600" aria-hidden="true" />
            Development connection check
          </h2>
          <p className="mt-3 text-sm text-slate-600" role="status">{status}</p>
          <button
            onClick={checkBackend}
            disabled={busy}
            className="mt-5 rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white transition-colors hover:bg-blue-700 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-blue-600 disabled:opacity-60"
          >
            {busy ? 'Checking...' : 'Check backend'}
          </button>
        </div>
      </section>
      <footer className="text-sm text-slate-500">
        NetSage development foundation
      </footer>
    </main>
  )
}
