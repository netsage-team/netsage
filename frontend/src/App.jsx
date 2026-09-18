import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  BellRing,
  ChevronRight,
  CircleAlert,
  Gauge,
  Globe2,
  LogOut,
  Moon,
  Network,
  RefreshCw,
  Router,
  Server,
  ShieldCheck,
  Sun,
  Users,
  Wifi,
} from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getCurrentUser,
  getJson,
  patchJson,
  postJson,
  resultsOf,
  signIn,
  signOut,
} from './api'


function formatDate(value) {
  if (!value) return 'Not available'

  return new Intl.DateTimeFormat('en-UG', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}


function shortTime(value) {
  if (!value) return ''

  return new Intl.DateTimeFormat('en-UG', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}


function severityClass(severity) {
  if (severity === 'critical') {
    return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900/50 dark:bg-red-950/50 dark:text-red-300'
  }

  return 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-300'
}


function statusLabel(status) {
  return String(status || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}


function Login({ onSignedIn, darkMode, toggleDarkMode }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')

    try {
      const data = await signIn(username, password)
      onSignedIn(data.user)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-white">
      <div className="grid min-h-screen lg:grid-cols-[1.08fr_0.92fr]">
        <section className="relative hidden overflow-hidden bg-slate-950 lg:block">
          <img
            src="/images/netsage-hero.png"
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-50"
          />

          <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/85 to-slate-950/30" />

          <div className="relative flex h-full max-w-3xl flex-col justify-between p-14 text-white">
            <div className="w-fit rounded-xl bg-white/95 px-3 py-2 shadow-sm">
              <img
                src="/images/netsage-logo.png"
                alt="NetSage"
                className="h-8 w-fit object-contain"
              />
            </div>

            <div className="pb-14">
              <p className="mb-5 text-sm font-semibold uppercase tracking-[0.22em] text-blue-300">
                Network monitoring and incident response
              </p>

              <h1 className="max-w-2xl text-5xl font-extrabold leading-[1.05] tracking-tight">
                Network clarity.
                <span className="mt-2 block text-red-400">
                  Connected communities.
                </span>
              </h1>

              <p className="mt-7 max-w-xl text-lg leading-8 text-slate-300">
                Detect service degradation, correlate related network
                problems and help operations teams respond with context.
              </p>

              <div className="mt-10 grid max-w-xl grid-cols-3 gap-3">
                <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                  <Activity className="mb-3 h-5 w-5 text-blue-300" />
                  <p className="text-sm font-semibold">Monitor</p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                  <CircleAlert className="mb-3 h-5 w-5 text-red-300" />
                  <p className="text-sm font-semibold">Detect</p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                  <ShieldCheck className="mb-3 h-5 w-5 text-emerald-300" />
                  <p className="text-sm font-semibold">Respond</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="flex min-h-screen items-center justify-center px-6 py-12">
          <div className="w-full max-w-md">
            <div className="mb-8 flex items-center justify-between lg:justify-end">
              <img
                src="/images/netsage-logo.png"
                alt="NetSage"
                className="h-10 w-fit object-contain lg:hidden"
              />

              <button
                type="button"
                onClick={toggleDarkMode}
                className="rounded-xl border border-slate-200 bg-white p-2.5 text-slate-600 transition hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
                aria-label="Toggle colour mode"
              >
                {darkMode ? <Sun size={19} /> : <Moon size={19} />}
              </button>
            </div>

            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
              Operations console
            </p>

            <h2 className="mt-3 text-3xl font-bold tracking-tight">
              Sign in to NetSage
            </h2>

            <p className="mt-3 text-slate-500 dark:text-slate-400">
              Staff access is required to view network incidents and
              operational data.
            </p>

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <div>
                <label
                  htmlFor="username"
                  className="mb-2 block text-sm font-semibold"
                >
                  Username
                </label>

                <input
                  id="username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  autoComplete="username"
                  required
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-900 dark:focus:ring-blue-950"
                  placeholder="operator"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-sm font-semibold"
                >
                  Password
                </label>

                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-900 dark:focus:ring-blue-950"
                  placeholder="Enter your password"
                />
              </div>

              {error && (
                <div
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/50 dark:text-red-300"
                >
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={busy}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3.5 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
              >
                {busy ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Signing in
                  </>
                ) : (
                  <>
                    Sign in
                    <ChevronRight size={18} />
                  </>
                )}
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  )
}


function StatCard({ icon: Icon, label, value, detail, danger = false }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-start justify-between">
        <div
          className={`rounded-xl p-2.5 ${
            danger
              ? 'bg-red-50 text-red-600 dark:bg-red-950/60 dark:text-red-400'
              : 'bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400'
          }`}
        >
          <Icon size={21} />
        </div>

        {danger && value > 0 && (
          <span className="rounded-full bg-red-100 px-2.5 py-1 text-xs font-semibold text-red-700 dark:bg-red-950 dark:text-red-300">
            Attention
          </span>
        )}
      </div>

      <p className="mt-5 text-sm font-medium text-slate-500 dark:text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-3xl font-bold tracking-tight">{value ?? '—'}</p>

      <p className="mt-2 text-xs text-slate-400">{detail}</p>
    </article>
  )
}


function TelemetryChart({ telemetry, metric, title, suffix }) {
  const threshold = metric === 'latency' ? 150 : 5

  const data = useMemo(() => {
    const grouped = new Map()

    for (const reading of telemetry) {
      const timestamp = reading.recorded_at

      const value =
        metric === 'latency'
          ? reading.latency_ms
          : reading.packet_loss_percent

      if (value === null || value === undefined) continue

      const existing = grouped.get(timestamp)

      if (!existing || value > existing.value) {
        grouped.set(timestamp, {
          timestamp,
          value,
          device: reading.device_name,
        })
      }
    }

    return [...grouped.values()]
      .sort(
        (a, b) =>
          new Date(a.timestamp).getTime() -
          new Date(b.timestamp).getTime()
      )
      .map((item) => ({
        ...item,
        time: shortTime(item.timestamp),
      }))
  }, [telemetry, metric])

  const peak = data.length
    ? Math.max(...data.map((item) => item.value))
    : null

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h3 className="font-bold">{title}</h3>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Peak network condition across the current view
          </p>
        </div>

        {peak !== null && (
          <div className="text-right">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Peak
            </p>
            <p
              className={`mt-1 text-lg font-bold ${
                peak > threshold
                  ? 'text-red-600 dark:text-red-400'
                  : 'text-emerald-600 dark:text-emerald-400'
              }`}
            >
              {peak.toFixed(metric === 'latency' ? 0 : 1)}
              {suffix}
            </p>
          </div>
        )}
      </div>

      <div className="h-64">
        {data.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="4 4"
                vertical={false}
              />

              <XAxis
                dataKey="time"
                tick={{ fontSize: 11 }}
                minTickGap={28}
              />

              <YAxis
                tick={{ fontSize: 11 }}
                width={52}
                domain={[0, 'auto']}
              />

              <Tooltip
                formatter={(value, name, item) => [
                  `${Number(value).toFixed(
                    metric === 'latency' ? 0 : 1
                  )}${suffix}`,
                  item?.payload?.device || title,
                ]}
                labelFormatter={(label) => `Time: ${label}`}
              />

              <ReferenceLine
                y={threshold}
                stroke="#dc2626"
                strokeDasharray="6 5"
                label={{
                  value: `Alert threshold ${threshold}${suffix}`,
                  position: 'insideTopRight',
                  fill: '#dc2626',
                  fontSize: 11,
                }}
              />

              <Line
                type="monotone"
                dataKey="value"
                stroke="#2563eb"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">
            No telemetry available for this view.
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center gap-4 text-xs text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-5 rounded-full bg-blue-600" />
          Observed peak
        </span>

        <span className="flex items-center gap-1.5">
          <span className="h-0 w-5 border-t-2 border-dashed border-red-600" />
          Alert threshold
        </span>

        <span>{telemetry.length} readings loaded</span>
      </div>
    </article>
  )
}


function CustomerUpdatePanel({ incident }) {
  const [audience, setAudience] = useState(null)
  const [messageType, setMessageType] = useState('outage')
  const [message, setMessage] = useState('')
  const [draft, setDraft] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [approving, setApproving] = useState(false)
  const [sending, setSending] = useState(false)
  const [history, setHistory] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const defaultMessages = useMemo(() => {
    const sites =
      incident.affected_site_names?.join(', ') ||
      incident.site_name ||
      'the affected area'

    return {
      outage:
        `We are investigating a network service issue affecting ${sites}. ` +
        'Our technical team is working to restore normal service.',

      update:
        `Our technical team is continuing to investigate the network issue affecting ${sites}. ` +
        'We will provide another update as work progresses.',

      recovery:
        `Network service affecting ${sites} has recovered and is being monitored. ` +
        'Thank you for your patience.',
    }
  }, [
    incident.affected_site_names,
    incident.site_name,
  ])

  async function loadAudience() {
    const data = await getJson(
      `/api/incidents/${incident.id}/notification-audience/`
    )

    setAudience(data)
  }

  async function loadDraft(type) {
    const data = await getJson(
      `/api/incidents/${incident.id}/notification-draft/?message_type=${encodeURIComponent(type)}`
    )

    setDraft(data)

    if (data.exists) {
      setMessage(data.message)
    } else {
      setMessage(defaultMessages[type])
    }
  }

  useEffect(() => {
    let active = true

    async function load() {
      setLoading(true)
      setError('')

      try {
        const [audienceData, draftData, historyData] =
          await Promise.all([
            getJson(
              `/api/incidents/${incident.id}/notification-audience/`
            ),
            getJson(
              `/api/incidents/${incident.id}/notification-draft/?message_type=${encodeURIComponent(messageType)}`
            ),
            getJson(
              `/api/incidents/${incident.id}/notification-history/?message_type=${encodeURIComponent(messageType)}`
            ),
          ])

        if (!active) return

        setAudience(audienceData)
        setDraft(draftData)
        setHistory(historyData)

        if (draftData.exists) {
          setMessage(draftData.message)
        } else {
          setMessage(defaultMessages[messageType])
        }
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    load()

    return () => {
      active = false
    }
  }, [
    incident.id,
    messageType,
    defaultMessages,
  ])

  async function loadHistory(type = messageType) {
    const data = await getJson(
      `/api/incidents/${incident.id}/notification-history/?message_type=${encodeURIComponent(type)}`
    )

    setHistory(data)
  }

  async function sendApproved() {
    setSending(true)
    setError('')
    setSuccess('')

    try {
      const data = await postJson(
        `/api/incidents/${incident.id}/notification-send/`,
        {
          message_type: messageType,
        }
      )

      await Promise.all([
        loadDraft(messageType),
        loadHistory(messageType),
      ])

      if (data.mode === 'dry_run') {
        setSuccess(
          `Dry run completed for ${data.dry_run_count} recipient${data.dry_run_count === 1 ? '' : 's'}. No external SMS was sent.`
        )
      } else {
        setSuccess(
          `${data.submitted_count} message${data.submitted_count === 1 ? '' : 's'} submitted to the SMS provider.`
        )
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  async function saveDraft() {
    if (!message.trim()) {
      setError('Enter a customer message first.')
      return
    }

    setSaving(true)
    setError('')
    setSuccess('')

    try {
      await postJson(
        `/api/incidents/${incident.id}/notification-draft/`,
        {
          message_type: messageType,
          message: message.trim(),
        }
      )

      await loadDraft(messageType)

      setSuccess(
        'Draft saved. It still requires operator approval before sending.'
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function approveDraft() {
    setApproving(true)
    setError('')
    setSuccess('')

    try {
      const data = await postJson(
        `/api/incidents/${incident.id}/notification-approve/`,
        {
          message_type: messageType,
        }
      )

      await Promise.all([
        loadDraft(messageType),
        loadHistory(messageType),
      ])

      setSuccess(
        `Approved by ${data.approved_by}. No SMS has been sent yet.`
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setApproving(false)
    }
  }

  if (loading) {
    return (
      <div className="mt-6 flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-950">
        <RefreshCw
          size={16}
          className="animate-spin"
        />
        Loading customer notification audience
      </div>
    )
  }

  return (
    <section className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-950">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div>
          <div className="flex items-center gap-2">
            <BellRing
              size={18}
              className="text-blue-600 dark:text-blue-400"
            />

            <h3 className="font-bold">
              Customer update
            </h3>
          </div>

          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Prepare an operator-approved SMS for customers on affected sites.
          </p>
        </div>

        <div className="rounded-xl bg-white px-4 py-3 text-right shadow-sm dark:bg-slate-900">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Eligible recipients
          </p>

          <p className="mt-1 text-2xl font-bold">
            {audience?.eligible_recipients ?? 0}
          </p>
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[0.75fr_1.25fr]">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Audience
          </p>

          <div className="mt-3 space-y-2">
            {audience?.affected_sites?.map((site) => (
              <div
                key={site.id}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-800 dark:bg-slate-900"
              >
                <span className="font-medium">
                  {site.name}
                </span>

                <span className="text-slate-400">
                  {site.eligible_recipients}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-4 space-y-2">
            {audience?.recipients?.map((recipient) => (
              <div
                key={recipient.id}
                className="text-xs text-slate-500 dark:text-slate-400"
              >
                <span className="font-medium text-slate-700 dark:text-slate-300">
                  {recipient.name}
                </span>
                {' · '}
                {recipient.phone}
              </div>
            ))}
          </div>
        </div>

        <div>
          <label
            htmlFor={`message-type-${incident.id}`}
            className="block text-sm font-semibold"
          >
            Message type
          </label>

          <select
            id={`message-type-${incident.id}`}
            value={messageType}
            onChange={(event) => {
              setMessageType(event.target.value)
              setSuccess('')
              setError('')
            }}
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-900"
          >
            <option value="outage">
              Outage notice
            </option>

            <option value="update">
              Progress update
            </option>

            <option value="recovery">
              Service restored
            </option>
          </select>

          <label
            htmlFor={`customer-message-${incident.id}`}
            className="mt-4 block text-sm font-semibold"
          >
            Message
          </label>

          <textarea
            id={`customer-message-${incident.id}`}
            rows={5}
            maxLength={480}
            value={message}
            onChange={(event) => {
              setMessage(event.target.value)

              if (
                draft?.approval_status === 'approved'
              ) {
                setDraft((current) => ({
                  ...current,
                  approval_status: 'pending',
                }))
              }
            }}
            className="mt-2 w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm leading-6 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-900"
          />

          <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs text-slate-400">
              {message.length}/480 characters
            </span>

            <span
              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                draft?.approval_status === 'approved'
                  ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                  : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
              }`}
            >
              {draft?.approval_status === 'approved'
                ? 'Approved'
                : 'Approval pending'}
            </span>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={saveDraft}
              disabled={
                saving ||
                !message.trim() ||
                !audience?.eligible_recipients
              }
              className="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold transition hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
            >
              {saving
                ? 'Saving draft...'
                : 'Save draft'}
            </button>

            <button
              type="button"
              onClick={approveDraft}
              disabled={
                approving ||
                !draft?.exists ||
                draft?.approval_status === 'approved'
              }
              className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
            >
              <ShieldCheck size={16} />

              {approving
                ? 'Approving...'
                : 'Approve message'}
            </button>
          </div>

          {draft?.approval_status === 'approved' && (
            <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-900 dark:bg-blue-950/40">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                    Ready for delivery
                  </p>

                  <p className="mt-1 text-xs leading-5 text-blue-700 dark:text-blue-300">
                    {audience?.sms_mode === 'dry_run'
                      ? 'Safe dry-run mode is active. No message will leave NetSage.'
                      : 'Sandbox mode is active. Only allowlisted test recipients can receive messages.'}
                  </p>
                </div>

                <span className="rounded-full bg-blue-100 px-2.5 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-900 dark:text-blue-200">
                  {audience?.sms_mode || 'unknown'}
                </span>
              </div>

              <button
                type="button"
                onClick={sendApproved}
                disabled={sending}
                className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
              >
                {sending ? (
                  <>
                    <RefreshCw
                      size={15}
                      className="animate-spin"
                    />
                    Processing
                  </>
                ) : audience?.sms_mode === 'dry_run' ? (
                  <>
                    <BellRing size={16} />
                    Run safe SMS dry run
                  </>
                ) : (
                  <>
                    <BellRing size={16} />
                    Send approved SMS
                  </>
                )}
              </button>
            </div>
          )}

          {history?.notifications?.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Delivery history
              </p>

              <div className="mt-2 space-y-2">
                {history.notifications.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-xs dark:border-slate-800 dark:bg-slate-900"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-slate-700 dark:text-slate-200">
                        {item.customer}
                      </p>

                      <p className="mt-0.5 text-slate-400">
                        {item.site} · {item.phone}
                      </p>
                    </div>

                    <span
                      className={`rounded-full px-2.5 py-1 font-semibold ${
                        item.delivery_status === 'dry_run'
                          ? 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
                          : item.delivery_status === 'delivered'
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                          : item.delivery_status === 'failed'
                          ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'
                          : 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                      }`}
                    >
                      {statusLabel(item.delivery_status)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4 rounded-xl border border-dashed border-slate-300 p-3 text-xs leading-5 text-slate-500 dark:border-slate-700 dark:text-slate-400">
            Approval does not send an SMS. Sending will remain a separate explicit action.
          </div>

          {success && (
            <p className="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-300">
              {success}
            </p>
          )}

          {error && (
            <p
              role="alert"
              className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/50 dark:text-red-300"
            >
              {error}
            </p>
          )}
        </div>
      </div>
    </section>
  )
}


function IncidentWorkspace({
  incident,
  engineers,
  onUpdated,
}) {
  const [engineerId, setEngineerId] = useState(
    incident.assigned_to ? String(incident.assigned_to) : ''
  )
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [noteBusy, setNoteBusy] = useState(false)
  const [recoveryBusy, setRecoveryBusy] = useState(false)
  const [resolveBusy, setResolveBusy] = useState(false)
  const [resolutionNotes, setResolutionNotes] = useState('')
  const [recoveryMessage, setRecoveryMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    setEngineerId(
      incident.assigned_to ? String(incident.assigned_to) : ''
    )
  }, [incident.assigned_to])

  async function assignAndInvestigate() {
    if (!engineerId) {
      setError('Select an engineer before starting investigation.')
      return
    }

    setBusy(true)
    setError('')

    try {
      await patchJson(
        `/api/incidents/${incident.id}/manage/`,
        {
          assigned_to: Number(engineerId),
          status: 'investigating',
        }
      )

      await onUpdated()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function addNote() {
    const trimmed = note.trim()

    if (!trimmed) {
      setError('Enter an investigation note first.')
      return
    }

    setNoteBusy(true)
    setError('')

    try {
      await postJson(
        `/api/incidents/${incident.id}/notes/`,
        {
          note: trimmed,
        }
      )

      setNote('')
      await onUpdated()
    } catch (err) {
      setError(err.message)
    } finally {
      setNoteBusy(false)
    }
  }

  async function verifyRecovery() {
    setRecoveryBusy(true)
    setError('')
    setRecoveryMessage('')

    try {
      const data = await postJson(
        `/api/incidents/${incident.id}/verify-recovery/`,
        {}
      )

      const recoveredSites =
        data.recovery?.sites?.length || 0

      setRecoveryMessage(
        `Sustained healthy telemetry verified across ${recoveredSites} affected site${recoveredSites === 1 ? '' : 's'}.`
      )

      await onUpdated()
    } catch (err) {
      setError(err.message)
    } finally {
      setRecoveryBusy(false)
    }
  }

  async function resolveIncident() {
    const trimmed = resolutionNotes.trim()

    if (!trimmed) {
      setError(
        'Add resolution notes before closing the incident.'
      )
      return
    }

    setResolveBusy(true)
    setError('')

    try {
      await postJson(
        `/api/incidents/${incident.id}/resolve/`,
        {
          resolution_notes: trimmed,
        }
      )

      setResolutionNotes('')
      await onUpdated()
    } catch (err) {
      setError(err.message)
    } finally {
      setResolveBusy(false)
    }
  }

  const timeline = [...(incident.timeline || [])].reverse()

  return (
    <div className="mt-5 border-t border-slate-100 pt-5 dark:border-slate-800">
      <div className="grid gap-5 lg:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Incident response
          </p>

          <label
            htmlFor={`engineer-${incident.id}`}
            className="mt-4 block text-sm font-semibold"
          >
            Assigned engineer
          </label>

          <select
            id={`engineer-${incident.id}`}
            value={engineerId}
            onChange={(event) => setEngineerId(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950"
          >
            <option value="">Select engineer</option>

            {engineers.map((engineer) => (
              <option
                key={engineer.id}
                value={engineer.id}
              >
                {engineer.first_name || engineer.last_name
                  ? `${engineer.first_name} ${engineer.last_name}`.trim()
                  : engineer.username}
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={assignAndInvestigate}
            disabled={
              busy ||
              !['open', 'investigating'].includes(incident.status)
            }
            className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? (
              <>
                <RefreshCw size={15} className="animate-spin" />
                Updating incident
              </>
            ) : (
              <>
                <Users size={16} />
                Assign and start investigation
              </>
            )}
          </button>

          <label
            htmlFor={`note-${incident.id}`}
            className="mt-5 block text-sm font-semibold"
          >
            Investigation note
          </label>

          <textarea
            id={`note-${incident.id}`}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            rows={4}
            maxLength={2000}
            placeholder="Example: Checking the Mukono uplink and upstream connectivity."
            className="mt-2 w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950"
          />

          <div className="mt-2 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              {note.length}/2000
            </span>

            <button
              type="button"
              onClick={addNote}
              disabled={noteBusy || !note.trim()}
              className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-800"
            >
              {noteBusy ? 'Saving...' : 'Add note'}
            </button>
          </div>

          {incident.status === 'investigating' && (
            <div className="mt-5 rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-900 dark:bg-blue-950/40">
              <p className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                Recovery verification
              </p>

              <p className="mt-1 text-xs leading-5 text-blue-700 dark:text-blue-300">
                Check whether all affected sites have maintained healthy telemetry for the configured recovery period.
              </p>

              <button
                type="button"
                onClick={verifyRecovery}
                disabled={recoveryBusy}
                className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
              >
                {recoveryBusy ? (
                  <>
                    <RefreshCw
                      size={15}
                      className="animate-spin"
                    />
                    Checking telemetry
                  </>
                ) : (
                  <>
                    <ShieldCheck size={16} />
                    Verify sustained recovery
                  </>
                )}
              </button>
            </div>
          )}

          {incident.status === 'monitoring' && (
            <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-900 dark:bg-emerald-950/40">
              <p className="text-sm font-semibold text-emerald-900 dark:text-emerald-100">
                Recovery verified
              </p>

              <p className="mt-1 text-xs leading-5 text-emerald-700 dark:text-emerald-300">
                Sustained healthy telemetry has been verified. The assigned engineer can now close the incident.
              </p>

              <label
                htmlFor={`resolution-${incident.id}`}
                className="mt-4 block text-sm font-semibold"
              >
                Resolution notes
              </label>

              <textarea
                id={`resolution-${incident.id}`}
                value={resolutionNotes}
                onChange={(event) =>
                  setResolutionNotes(event.target.value)
                }
                rows={3}
                maxLength={2000}
                placeholder="Describe what was verified before closure."
                className="mt-2 w-full resize-none rounded-xl border border-emerald-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-500 dark:border-emerald-900 dark:bg-slate-950"
              />

              <button
                type="button"
                onClick={resolveIncident}
                disabled={
                  resolveBusy || !resolutionNotes.trim()
                }
                className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
              >
                {resolveBusy ? (
                  <>
                    <RefreshCw
                      size={15}
                      className="animate-spin"
                    />
                    Resolving
                  </>
                ) : (
                  <>
                    <ShieldCheck size={16} />
                    Resolve incident
                  </>
                )}
              </button>
            </div>
          )}

          {recoveryMessage && (
            <p className="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-300">
              {recoveryMessage}
            </p>
          )}

          {error && (
            <p
              role="alert"
              className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/50 dark:text-red-300"
            >
              {error}
            </p>
          )}
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Activity timeline
          </p>

          <div className="mt-4 space-y-4">
            {timeline.length ? (
              timeline.map((event) => (
                <div
                  key={event.id}
                  className="relative flex gap-3"
                >
                  <div className="flex flex-col items-center">
                    <span
                      className={`mt-1 h-3 w-3 rounded-full ${
                        event.event_type === 'detected'
                          ? 'bg-red-500'
                          : event.event_type === 'note'
                          ? 'bg-amber-500'
                          : 'bg-blue-600'
                      }`}
                    />

                    <span className="mt-1 h-full w-px bg-slate-200 dark:bg-slate-700" />
                  </div>

                  <div className="min-w-0 flex-1 pb-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-semibold">
                        {statusLabel(event.event_type)}
                      </p>

                      <span className="text-xs text-slate-400">
                        {formatDate(event.created_at)}
                      </span>
                    </div>

                    <p className="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">
                      {event.message}
                    </p>

                    {event.actor_name && (
                      <p className="mt-1 text-xs font-medium text-blue-600 dark:text-blue-400">
                        By {event.actor_name}
                      </p>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400">
                No incident activity recorded yet.
              </p>
            )}
          </div>
        </div>
      </div>

      <CustomerUpdatePanel
        incident={incident}
      />
    </div>
  )
}


function Dashboard({
  user,
  darkMode,
  toggleDarkMode,
  onSignedOut,
}) {
  const [sites, setSites] = useState([])
  const [selectedSite, setSelectedSite] = useState('')
  const [summary, setSummary] = useState(null)
  const [devices, setDevices] = useState([])
  const [telemetry, setTelemetry] = useState([])
  const [alerts, setAlerts] = useState([])
  const [incidents, setIncidents] = useState([])
  const [engineers, setEngineers] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  async function loadSites() {
    const data = await getJson('/api/sites/')
    setSites(resultsOf(data))
  }

  async function loadEngineers() {
    const data = await getJson('/api/engineers/')
    setEngineers(resultsOf(data))
  }

  async function loadDashboard(showRefresh = false) {
    if (showRefresh) setRefreshing(true)
    else setLoading(true)

    setError('')

    const query = selectedSite
      ? `?site=${encodeURIComponent(selectedSite)}`
      : ''

    const telemetryQuery = selectedSite
      ? `?site=${encodeURIComponent(selectedSite)}&page_size=200`
      : '?page_size=200'

    try {
      const [
        summaryData,
        deviceData,
        telemetryData,
        alertData,
        incidentData,
      ] = await Promise.all([
        getJson(`/api/dashboard/summary/${query}`),
        getJson(`/api/devices/${query}`),
        getJson(`/api/telemetry/${telemetryQuery}`),
        getJson(`/api/alerts/${query}`),
        getJson(`/api/incidents/${query}`),
      ])

      setSummary(summaryData)
      setDevices(resultsOf(deviceData))
      setTelemetry(resultsOf(telemetryData))
      setAlerts(resultsOf(alertData))
      setIncidents(resultsOf(incidentData))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    Promise.all([
      loadSites(),
      loadEngineers(),
    ]).catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    loadDashboard()
  }, [selectedSite])

  async function handleLogout() {
    try {
      await signOut()
    } finally {
      onSignedOut()
    }
  }

  const activeAlerts = alerts.filter((alert) => !alert.cleared_at)
  const activeIncidents = incidents.filter(
    (incident) => incident.status !== 'resolved'
  )
  const criticalIncident = incidents.find(
    (incident) =>
      incident.severity === 'critical' &&
      incident.status !== 'resolved'
  )

  const currentSiteName =
    sites.find((site) => String(site.id) === String(selectedSite))?.name ||
    'All monitored sites'

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-slate-100">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between px-5 py-3 lg:px-8">
          <div className="flex items-center gap-5">
            <img
              src="/images/netsage-logo.png"
              alt="NetSage"
              className="h-9 w-fit object-contain"
            />

            <span className="hidden border-l border-slate-200 pl-5 text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400 md:block">
              Network Operations
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={toggleDarkMode}
              className="rounded-xl p-2.5 text-slate-500 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900"
              aria-label="Toggle colour mode"
            >
              {darkMode ? <Sun size={19} /> : <Moon size={19} />}
            </button>

            <div className="hidden px-3 text-right sm:block">
              <p className="text-sm font-semibold">
                {user.first_name || user.username}
              </p>
              <p className="text-xs text-slate-400">Operations staff</p>
            </div>

            <button
              type="button"
              onClick={handleLogout}
              className="rounded-xl p-2.5 text-slate-500 transition hover:bg-slate-100 hover:text-red-600 dark:text-slate-300 dark:hover:bg-slate-900"
              aria-label="Sign out"
            >
              <LogOut size={19} />
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1500px] px-5 py-7 lg:px-8">
        <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-blue-600 dark:text-blue-400">
              <Activity size={16} />
              Live network operations
            </div>

            <h1 className="mt-2 text-3xl font-bold tracking-tight">
              Operations dashboard
            </h1>

            <p className="mt-2 text-slate-500 dark:text-slate-400">
              Monitor service health, correlated alerts and active incidents.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <select
              value={selectedSite}
              onChange={(event) => setSelectedSite(event.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium outline-none dark:border-slate-800 dark:bg-slate-900"
            >
              <option value="">All monitored sites</option>
              {sites.map((site) => (
                <option key={site.id} value={site.id}>
                  {site.name}
                </option>
              ))}
            </select>

            <button
              type="button"
              onClick={() => loadDashboard(true)}
              disabled={refreshing}
              className="flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
            >
              <RefreshCw
                size={16}
                className={refreshing ? 'animate-spin' : ''}
              />
              Refresh
            </button>
          </div>
        </section>

        {error && (
          <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/50 dark:text-red-300">
            {error}
          </div>
        )}

        {criticalIncident && (
          <section className="mt-6 overflow-hidden rounded-2xl border border-red-200 bg-red-50 dark:border-red-900/60 dark:bg-red-950/40">
            <div className="flex flex-col gap-4 p-5 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex gap-4">
                <div className="mt-0.5 rounded-xl bg-red-100 p-2.5 text-red-600 dark:bg-red-950 dark:text-red-300">
                  <AlertTriangle size={22} />
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-bold text-red-950 dark:text-red-100">
                      Critical correlated incident detected
                    </h2>

                    <span className="rounded-full bg-red-200/70 px-2.5 py-1 text-xs font-bold uppercase text-red-800 dark:bg-red-900 dark:text-red-200">
                      {criticalIncident.status}
                    </span>
                  </div>

                  <p className="mt-1 text-sm text-red-800 dark:text-red-300">
                    {criticalIncident.title}
                  </p>

                  {criticalIncident.shared_dependency && (
                    <p className="mt-2 text-xs font-semibold text-red-700 dark:text-red-400">
                      Shared dependency: {criticalIncident.shared_dependency}
                    </p>
                  )}
                </div>
              </div>

              <div className="text-sm text-red-700 dark:text-red-300">
                {criticalIncident.affected_site_names?.length || 0} affected sites
              </div>
            </div>
          </section>
        )}

        <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            icon={Globe2}
            label="Active sites"
            value={summary?.sites_active}
            detail={currentSiteName}
          />

          <StatCard
            icon={Router}
            label="Active devices"
            value={summary?.devices_active}
            detail={`${devices.length} visible in current view`}
          />

          <StatCard
            icon={BellRing}
            label="Active alerts"
            value={summary?.alerts_active}
            detail={`${summary?.alerts_critical ?? 0} critical`}
            danger={(summary?.alerts_active ?? 0) > 0}
          />

          <StatCard
            icon={CircleAlert}
            label="Active incidents"
            value={summary?.incidents_active}
            detail={`${summary?.incidents_unassigned ?? 0} unassigned`}
            danger={(summary?.incidents_active ?? 0) > 0}
          />
        </section>

        {loading ? (
          <div className="mt-10 flex items-center justify-center gap-3 py-20 text-slate-500">
            <RefreshCw className="animate-spin" size={20} />
            Loading network data
          </div>
        ) : (
          <>
            <section className="mt-6 grid gap-6 xl:grid-cols-2">
              <TelemetryChart
                telemetry={telemetry}
                metric="latency"
                title="Latency"
                suffix=" ms"
              />

              <TelemetryChart
                telemetry={telemetry}
                metric="loss"
                title="Packet loss"
                suffix="%"
              />
            </section>

            <section className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <article className="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <div className="border-b border-slate-100 px-5 py-4 dark:border-slate-800">
                  <div className="flex items-center gap-2">
                    <CircleAlert className="text-red-500" size={19} />
                    <h2 className="font-bold">Active incidents</h2>
                  </div>

                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Correlated network issues requiring investigation
                  </p>
                </div>

                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {activeIncidents.length ? (
                    activeIncidents.map((incident) => (
                      <div key={incident.id} className="p-5">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <h3 className="font-semibold">
                              {incident.title}
                            </h3>

                            <div className="mt-2 flex flex-wrap gap-2">
                              <span
                                className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${severityClass(
                                  incident.severity
                                )}`}
                              >
                                {incident.severity}
                              </span>

                              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                                {statusLabel(incident.status)}
                              </span>
                            </div>

                            <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                              Engineer:{' '}
                              <span className="font-semibold text-slate-700 dark:text-slate-200">
                                {incident.assigned_to_name || 'Unassigned'}
                              </span>
                            </p>
                          </div>

                          <span className="text-xs text-slate-400">
                            {formatDate(incident.opened_at)}
                          </span>
                        </div>

                        {incident.affected_site_names?.length > 0 && (
                          <div className="mt-4">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                              Affected sites
                            </p>

                            <div className="mt-2 flex flex-wrap gap-2">
                              {incident.affected_site_names.map((name) => (
                                <span
                                  key={name}
                                  className="rounded-lg bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 dark:bg-blue-950/60 dark:text-blue-300"
                                >
                                  {name}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {incident.probable_cause && (
                          <div className="mt-4 rounded-xl bg-slate-50 p-4 dark:bg-slate-950">
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                              Probable cause
                            </p>

                            <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
                              {incident.probable_cause}
                            </p>

                            {incident.confidence_note && (
                              <p className="mt-2 text-xs leading-5 text-slate-500">
                                {incident.confidence_note}
                              </p>
                            )}
                          </div>
                        )}

                        <IncidentWorkspace
                          incident={incident}
                          engineers={engineers}
                          onUpdated={() => loadDashboard(true)}
                        />
                      </div>
                    ))
                  ) : (
                    <div className="p-10 text-center text-sm text-slate-400">
                      No incidents in this view.
                    </div>
                  )}
                </div>
              </article>

              <article className="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <div className="border-b border-slate-100 px-5 py-4 dark:border-slate-800">
                  <div className="flex items-center gap-2">
                    <BellRing className="text-amber-500" size={19} />
                    <h2 className="font-bold">Recent alerts</h2>
                  </div>

                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Sustained faults detected by NetSage
                  </p>
                </div>

                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {activeAlerts.length ? (
                    activeAlerts.map((alert) => (
                      <div key={alert.id} className="p-5">
                        <div className="flex items-start gap-3">
                          <span className="mt-1 h-2.5 w-2.5 flex-none rounded-full bg-red-500" />

                          <div className="min-w-0 flex-1">
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <p className="font-semibold">
                                  {alert.device_name}
                                </p>

                                <p className="mt-1 text-xs font-medium uppercase tracking-wide text-red-500">
                                  {statusLabel(alert.alert_type)}
                                </p>
                              </div>

                              <span className="text-xs text-slate-400">
                                {shortTime(alert.detected_at)}
                              </span>
                            </div>

                            <p className="mt-3 text-sm leading-6 text-slate-500 dark:text-slate-400">
                              {alert.message}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-10 text-center text-sm text-slate-400">
                      No active alerts in this view.
                    </div>
                  )}
                </div>
              </article>
            </section>

            <section className="mt-6 grid gap-4 md:grid-cols-3">
              {sites.map((site) => {
                const siteAlerts = activeAlerts.filter(
                  (alert) => Number(alert.site) === Number(site.id)
                )

                return (
                  <article
                    key={site.id}
                    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
                  >
                    <div className="flex items-center justify-between">
                      <div className="rounded-xl bg-blue-50 p-2.5 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400">
                        <Wifi size={20} />
                      </div>

                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                          siteAlerts.length
                            ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'
                            : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                        }`}
                      >
                        {siteAlerts.length ? 'Degraded' : 'Healthy'}
                      </span>
                    </div>

                    <h3 className="mt-4 font-bold">{site.name}</h3>
                    <p className="mt-1 text-sm text-slate-500">
                      {site.location}
                    </p>

                    <div className="mt-4 flex items-center gap-2 text-xs text-slate-400">
                      <Network size={14} />
                      {siteAlerts.length} active alert
                      {siteAlerts.length === 1 ? '' : 's'}
                    </div>
                  </article>
                )
              })}
            </section>

            <footer className="mt-8 flex flex-col justify-between gap-2 border-t border-slate-200 py-6 text-xs text-slate-400 dark:border-slate-800 sm:flex-row">
              <span>NetSage Network Operations</span>
              <span>
                {summary?.generated_at
                  ? `Updated ${formatDate(summary.generated_at)}`
                  : ''}
              </span>
            </footer>
          </>
        )}
      </main>
    </div>
  )
}


export default function App() {
  const [user, setUser] = useState(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('netsage-theme') === 'dark'
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem(
      'netsage-theme',
      darkMode ? 'dark' : 'light'
    )
  }, [darkMode])

  useEffect(() => {
    getCurrentUser()
      .then((data) => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setCheckingSession(false))
  }, [])

  if (checkingSession) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="flex items-center gap-3 text-sm font-medium text-slate-500">
          <RefreshCw className="animate-spin" size={18} />
          Loading NetSage
        </div>
      </main>
    )
  }

  if (!user) {
    return (
      <Login
        darkMode={darkMode}
        toggleDarkMode={() => setDarkMode((value) => !value)}
        onSignedIn={setUser}
      />
    )
  }

  return (
    <Dashboard
      user={user}
      darkMode={darkMode}
      toggleDarkMode={() => setDarkMode((value) => !value)}
      onSignedOut={() => setUser(null)}
    />
  )
}
