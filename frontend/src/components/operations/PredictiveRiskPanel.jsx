import {
  Activity,
  AlertTriangle,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react'


function riskStyle(level) {
  if (level === 'critical') {
    return {
      card: 'border-red-300 bg-red-50 dark:border-red-900 dark:bg-red-950/40',
      text: 'text-red-900 dark:text-red-100',
      accent: 'text-red-600 dark:text-red-400',
      badge:
        'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
    }
  }

  if (level === 'high') {
    return {
      card:
        'border-orange-300 bg-orange-50 dark:border-orange-900 dark:bg-orange-950/40',
      text:
        'text-orange-900 dark:text-orange-100',
      accent:
        'text-orange-600 dark:text-orange-400',
      badge:
        'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300',
    }
  }

  if (level === 'medium') {
    return {
      card:
        'border-amber-300 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/40',
      text:
        'text-amber-900 dark:text-amber-100',
      accent:
        'text-amber-600 dark:text-amber-400',
      badge:
        'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
    }
  }

  return {
    card:
      'border-emerald-200 bg-emerald-50 dark:border-emerald-900 dark:bg-emerald-950/40',
    text:
      'text-emerald-900 dark:text-emerald-100',
    accent:
      'text-emerald-600 dark:text-emerald-400',
    badge:
      'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',
  }
}


function formatMetric(value, suffix) {
  if (
    value === null ||
    value === undefined
  ) {
    return 'Unknown'
  }

  return `${Number(value).toFixed(1)}${suffix}`
}


export default function PredictiveRiskPanel({
  data,
  loading = false,
  onRefresh,
}) {
  const warnings = data?.warnings || []
  const highestRisk = data?.highest_risk

  return (
    <section className="mt-6 rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-100 px-5 py-4 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Activity
              size={19}
              className="text-blue-600 dark:text-blue-400"
            />

            <h2 className="font-bold">
              Predictive network risk
            </h2>
          </div>

          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Early warning from latency, packet loss and
            reachability trends.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {data && (
            <div className="text-right">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Sites at risk
              </p>

              <p className="text-xl font-bold">
                {data.warning_count ?? 0}
              </p>
            </div>
          )}

          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-800"
            >
              <RefreshCw
                size={15}
                className={
                  loading
                    ? 'animate-spin'
                    : ''
                }
              />

              Refresh
            </button>
          )}
        </div>
      </div>

      <div className="p-5">
        {loading && !data ? (
          <div className="flex items-center gap-2 py-4 text-sm text-slate-500">
            <RefreshCw
              size={17}
              className="animate-spin"
            />

            Analysing network telemetry
          </div>
        ) : warnings.length === 0 ? (
          <div className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-900 dark:bg-emerald-950/40">
            <ShieldCheck
              size={21}
              className="mt-0.5 shrink-0 text-emerald-600 dark:text-emerald-400"
            />

            <div>
              <p className="font-semibold text-emerald-900 dark:text-emerald-100">
                No current pre-failure warning
              </p>

              <p className="mt-1 text-sm leading-6 text-emerald-700 dark:text-emerald-300">
                {highestRisk
                  ? `Highest current risk is ${highestRisk.site_name} at ${highestRisk.risk_score}/100.`
                  : 'No telemetry is available yet.'}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {warnings.map((site) => {
              const style = riskStyle(
                site.risk_level,
              )

              return (
                <article
                  key={site.site_id}
                  className={`rounded-2xl border p-5 ${style.card}`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <AlertTriangle
                        size={22}
                        className={`mt-0.5 shrink-0 ${style.accent}`}
                      />

                      <div>
                        <p
                          className={`text-xs font-bold uppercase tracking-wider ${style.accent}`}
                        >
                          Predictive warning
                        </p>

                        <h3
                          className={`mt-1 text-lg font-bold ${style.text}`}
                        >
                          {site.site_name}
                        </h3>

                        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                          {site.location}
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <div
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase ${style.badge}`}
                      >
                        {site.risk_level} risk
                      </div>

                      <p
                        className={`mt-2 text-3xl font-bold ${style.text}`}
                      >
                        {site.risk_score}
                        <span className="text-sm font-medium opacity-60">
                          /100
                        </span>
                      </p>
                    </div>
                  </div>

                  {site.predicted_failure && (
                    <div className="mt-4 rounded-xl border border-white/60 bg-white/60 px-4 py-3 dark:border-slate-800 dark:bg-slate-950/30">
                      <div className="flex items-center gap-2">
                        <TrendingUp
                          size={17}
                          className={style.accent}
                        />

                        <p
                          className={`text-sm font-bold ${style.text}`}
                        >
                          Possible service failure
                          approaching
                        </p>
                      </div>

                      <p className="mt-1 text-xs leading-5 text-slate-600 dark:text-slate-300">
                        The site is still reachable, but
                        recent telemetry shows worsening
                        conditions.
                      </p>
                    </div>
                  )}

                  <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="rounded-xl bg-white/70 p-3 dark:bg-slate-950/30">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Latency
                      </p>

                      <p className="mt-1 font-bold">
                        {formatMetric(
                          site.latest_latency_ms,
                          ' ms',
                        )}
                      </p>
                    </div>

                    <div className="rounded-xl bg-white/70 p-3 dark:bg-slate-950/30">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Packet loss
                      </p>

                      <p className="mt-1 font-bold">
                        {formatMetric(
                          site.latest_packet_loss_percent,
                          '%',
                        )}
                      </p>
                    </div>

                    <div className="rounded-xl bg-white/70 p-3 dark:bg-slate-950/30">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Latency trend
                      </p>

                      <p className="mt-1 font-bold">
                        {Number(
                          site.latency_trend || 0,
                        ).toFixed(2)}
                      </p>
                    </div>

                    <div className="rounded-xl bg-white/70 p-3 dark:bg-slate-950/30">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Reachable
                      </p>

                      <p className="mt-1 font-bold">
                        {site.is_reachable
                          ? 'Yes'
                          : 'No'}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 grid gap-4 lg:grid-cols-2">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Why NetSage raised this warning
                      </p>

                      <ul className="mt-2 space-y-1.5 text-sm leading-5 text-slate-700 dark:text-slate-300">
                        {(site.reasons || []).map(
                          (reason) => (
                            <li key={reason}>
                              • {reason}
                            </li>
                          ),
                        )}
                      </ul>
                    </div>

                    <div className="rounded-xl bg-white/70 p-4 dark:bg-slate-950/30">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Recommended response
                      </p>

                      <p className="mt-2 text-sm font-medium leading-6 text-slate-700 dark:text-slate-300">
                        {site.recommended_action}
                      </p>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        )}

        <p className="mt-4 text-xs leading-5 text-slate-400">
          Prediction currently uses explainable telemetry
          trend analysis. A production deployment can
          calibrate the model using historical operator
          network data.
        </p>
      </div>
    </section>
  )
}