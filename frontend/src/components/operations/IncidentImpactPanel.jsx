import { useEffect, useState } from 'react'
import {
  AlertTriangle,
  BellRing,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Users,
  Wrench,
} from 'lucide-react'

import {
  getJson,
  postJson,
} from '../../api'


function escalationClass(level) {
  if (level === 'level_3') {
    return 'border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300'
  }

  if (level === 'level_2') {
    return 'border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-900 dark:bg-orange-950/40 dark:text-orange-300'
  }

  if (level === 'level_1') {
    return 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300'
  }

  return 'border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
}


function formatTime(value) {
  if (!value) return 'Not yet'

  return new Intl.DateTimeFormat(
    'en-UG',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    },
  ).format(
    new Date(value),
  )
}


function Metric({
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-xl font-bold">
        {value}
      </p>
    </div>
  )
}


export default function IncidentImpactPanel({
  incident,
}) {
  const [impact, setImpact] = useState(null)
  const [loading, setLoading] = useState(true)
  const [automating, setAutomating] = useState(false)
  const [error, setError] = useState('')
  const [automaticMessage, setAutomaticMessage] = useState('')

  async function loadImpact() {
    setLoading(true)
    setError('')

    try {
      const data = await getJson(
        `/api/incidents/${incident.id}/impact/`,
      )

      setImpact(data)

      return data
    } catch (err) {
      setError(
        err.message ||
        'Could not load incident impact.',
      )

      return null
    } finally {
      setLoading(false)
    }
  }


  async function applyAutomaticEscalation(
    currentImpact,
  ) {
    if (!currentImpact) return

    const current = (
      currentImpact.maintenance
        ?.escalation_level
    )

    const recommended = (
      currentImpact.recommended_escalation
        ?.level
    )

    if (
      !recommended ||
      recommended === 'none' ||
      current === recommended
    ) {
      return
    }

    setAutomating(true)
    setError('')

    try {
      const updated = await postJson(
        `/api/incidents/${incident.id}/impact/`,
        {
          automatic: true,
        },
      )

      setImpact(updated)

      setAutomaticMessage(
        'NetSage automatically escalated this incident based on network and customer impact.',
      )
    } catch (err) {
      setError(
        err.message ||
        'Automatic escalation failed.',
      )
    } finally {
      setAutomating(false)
    }
  }


  useEffect(() => {
    let cancelled = false

    async function initialise() {
      const data = await loadImpact()

      if (
        !cancelled &&
        data
      ) {
        await applyAutomaticEscalation(
          data,
        )
      }
    }

    initialise()

    return () => {
      cancelled = true
    }
  }, [incident.id])


  if (
    loading &&
    !impact
  ) {
    return (
      <div className="mt-5 flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-950">
        <RefreshCw
          size={16}
          className="animate-spin"
        />

        Analysing incident impact
      </div>
    )
  }


  if (
    error &&
    !impact
  ) {
    return (
      <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
        {error}
      </div>
    )
  }


  if (!impact) {
    return null
  }


  const network = (
    impact.network_impact || {}
  )

  const maintenance = (
    impact.maintenance || {}
  )

  const recommendation = (
    impact.recommended_escalation || {}
  )

  const communication = (
    impact.communication || {}
  )


  return (
    <section className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-950">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck
              size={18}
              className="text-blue-600 dark:text-blue-400"
            />

            <h3 className="font-bold">
              Incident impact and automated response
            </h3>
          </div>

          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Network impact, customer exposure and
            maintenance escalation calculated by NetSage.
          </p>
        </div>

        <button
          type="button"
          onClick={loadImpact}
          disabled={
            loading ||
            automating
          }
          className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
        >
          <RefreshCw
            size={15}
            className={
              loading
                ? 'animate-spin'
                : ''
            }
          />

          Refresh impact
        </button>
      </div>


      {automaticMessage && (
        <div className="mt-4 flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-blue-800 dark:border-blue-900 dark:bg-blue-950/40 dark:text-blue-200">
          <Wrench
            size={18}
            className="mt-0.5 shrink-0"
          />

          <div>
            <p className="text-sm font-bold">
              Automated maintenance escalation
            </p>

            <p className="mt-1 text-xs leading-5">
              {automaticMessage}
            </p>
          </div>
        </div>
      )}


      {error && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}


      <div className="mt-5">
        <div className="flex items-center gap-2">
          <MapPin
            size={17}
            className="text-blue-600"
          />

          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Network and customer impact
          </p>
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Metric
            label="Affected sites"
            value={
              network.affected_site_count ?? 0
            }
          />

          <Metric
            label="Affected areas"
            value={
              network.affected_area_count ?? 0
            }
          />

          <Metric
            label="Customers potentially affected"
            value={
              network.potentially_affected_customers ?? 0
            }
          />

          <Metric
            label="Customer reports"
            value={
              network.customer_reports_received ?? 0
            }
          />
        </div>


        {impact.site_breakdown?.length > 0 && (
          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            {impact.site_breakdown.map(
              (site) => (
                <div
                  key={site.site_id}
                  className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
                >
                  <p className="font-semibold">
                    {site.site_name}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    {site.location}
                  </p>

                  <div className="mt-3 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                    <p>
                      Customers:{' '}
                      <strong>
                        {
                          site.potentially_affected_customers
                        }
                      </strong>
                    </p>

                    <p>
                      SMS eligible:{' '}
                      <strong>
                        {
                          site.sms_eligible_customers
                        }
                      </strong>
                    </p>

                    <p>
                      Reports:{' '}
                      <strong>
                        {
                          site.customer_reports
                        }
                      </strong>
                    </p>
                  </div>
                </div>
              ),
            )}
          </div>
        )}
      </div>


      <div className="mt-6 border-t border-slate-200 pt-5 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <Wrench
            size={17}
            className="text-orange-600"
          />

          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Maintenance response
          </p>
        </div>


        <div className="mt-3 grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Current escalation
            </p>

            <div className="mt-3 flex flex-wrap gap-2">
              <span
                className={`rounded-full border px-3 py-1 text-xs font-bold ${escalationClass(
                  maintenance.escalation_level,
                )}`}
              >
                {
                  maintenance.escalation_level_label ||
                  'Not escalated'
                }
              </span>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                {
                  maintenance.escalation_status_label ||
                  'Not escalated'
                }
              </span>
            </div>

            <div className="mt-4 space-y-2 text-sm">
              <p>
                <span className="text-slate-400">
                  Team:
                </span>{' '}
                <strong>
                  {
                    maintenance.escalation_team ||
                    'Not assigned'
                  }
                </strong>
              </p>

              <p>
                <span className="text-slate-400">
                  Engineer:
                </span>{' '}
                <strong>
                  {
                    maintenance.assigned_engineer ||
                    'Not assigned'
                  }
                </strong>
              </p>

              <p>
                <span className="text-slate-400">
                  Escalated:
                </span>{' '}
                <strong>
                  {formatTime(
                    maintenance.escalated_at,
                  )}
                </strong>
              </p>
            </div>
          </div>


          <div className="rounded-xl border border-orange-200 bg-orange-50 p-4 dark:border-orange-900 dark:bg-orange-950/30">
            <div className="flex items-start gap-2">
              <AlertTriangle
                size={18}
                className="mt-0.5 shrink-0 text-orange-600"
              />

              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-orange-600 dark:text-orange-400">
                  NetSage recommendation
                </p>

                <p className="mt-2 font-bold text-orange-900 dark:text-orange-100">
                  {
                    recommendation.level_label ||
                    'No escalation'
                  }
                </p>

                <p className="mt-1 text-sm font-medium text-orange-800 dark:text-orange-200">
                  {
                    recommendation.team ||
                    'Continue automated monitoring'
                  }
                </p>
              </div>
            </div>

            <p className="mt-3 text-sm leading-6 text-orange-800 dark:text-orange-200">
              {
                recommendation.recommended_response
              }
            </p>

            {recommendation.reasons?.length > 0 && (
              <ul className="mt-3 space-y-1 text-xs leading-5 text-orange-700 dark:text-orange-300">
                {recommendation.reasons.map(
                  (reason) => (
                    <li key={reason}>
                      • {reason}
                    </li>
                  ),
                )}
              </ul>
            )}

            {automating && (
              <div className="mt-3 flex items-center gap-2 text-xs font-semibold text-orange-700">
                <RefreshCw
                  size={14}
                  className="animate-spin"
                />

                Applying automatic escalation
              </div>
            )}
          </div>
        </div>
      </div>


      <div className="mt-6 border-t border-slate-200 pt-5 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <BellRing
            size={17}
            className="text-blue-600"
          />

          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Customer communication
          </p>
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <Metric
            label="SMS eligible"
            value={
              network.sms_eligible_customers ?? 0
            }
          />

          <Metric
            label="Prepared"
            value={
              communication.notification_records ?? 0
            }
          />

          <Metric
            label="Sent"
            value={
              communication.sent ?? 0
            }
          />

          <Metric
            label="Delivered"
            value={
              communication.delivered ?? 0
            }
          />

          <Metric
            label="Failed"
            value={
              communication.failed ?? 0
            }
          />

          <Metric
            label="Dry run"
            value={
              communication.dry_run ?? 0
            }
          />
        </div>
      </div>


      <div className="mt-5 flex items-start gap-2 rounded-xl bg-white p-3 text-xs leading-5 text-slate-500 dark:bg-slate-900 dark:text-slate-400">
        <Users
          size={15}
          className="mt-0.5 shrink-0"
        />

        Customer impact is calculated from active
        NetSage customer records associated with affected
        sites. Maintenance escalation is generated using
        explainable operational rules.
      </div>
    </section>
  )
}