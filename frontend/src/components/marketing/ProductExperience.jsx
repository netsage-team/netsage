import {
  Activity,
  ArrowRight,
  CheckCircle2,
  GitMerge,
  MessageSquareText,
  Network,
  Search,
  Wrench,
} from 'lucide-react'
import { Link } from 'react-router-dom'

const workflowSteps = [
  {
    number: '01',
    title: 'Monitor',
    description:
      'Collect latency, packet loss and service-health telemetry across sites and devices.',
    icon: Activity,
  },
  {
    number: '02',
    title: 'Detect',
    description:
      'Identify sustained degradation without reacting to every temporary spike.',
    icon: Search,
  },
  {
    number: '03',
    title: 'Correlate',
    description:
      'Group related alerts and surface evidence of a probable shared dependency.',
    icon: GitMerge,
  },
  {
    number: '04',
    title: 'Respond',
    description:
      'Create an incident, assign engineers and record investigation activity.',
    icon: Wrench,
  },
  {
    number: '05',
    title: 'Communicate',
    description:
      'Send approved customer outage updates through SMS and track delivery.',
    icon: MessageSquareText,
  },
  {
    number: '06',
    title: 'Verify',
    description:
      'Confirm sustained network recovery before resolving the incident.',
    icon: CheckCircle2,
  },
]

const scatteredAlerts = [
  'Tower A degradation',
  'Tower B packet loss',
  'Tower C latency alert',
]

export default function ProductExperience() {
  return (
    <>
      <section
        id="how-it-works"
        className="scroll-mt-24 bg-white py-24 dark:bg-slate-950"
      >
        <div className="mx-auto max-w-7xl px-5 lg:px-8">
          <div className="max-w-3xl">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
              How NetSage works
            </p>

            <h2 className="mt-4 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
              From signal to action
            </h2>

            <p className="mt-5 text-lg leading-8 text-slate-600 dark:text-slate-300">
              NetSage turns network telemetry into a coordinated incident
              response workflow.
            </p>
          </div>

          <div className="relative mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {workflowSteps.map((step) => {
              const Icon = step.icon

              return (
                <article
                  key={step.title}
                  className="relative rounded-2xl border border-slate-200 bg-slate-50 p-6 dark:border-slate-800 dark:bg-slate-900"
                >
                  <div className="flex items-center justify-between">
                    <div className="rounded-xl bg-blue-100 p-3 text-blue-600 dark:bg-blue-950 dark:text-blue-300">
                      <Icon size={23} aria-hidden="true" />
                    </div>

                    <span className="text-sm font-black text-slate-300 dark:text-slate-600">
                      {step.number}
                    </span>
                  </div>

                  <h3 className="mt-5 text-xl font-bold text-slate-950 dark:text-white">
                    {step.title}
                  </h3>

                  <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
                    {step.description}
                  </p>
                </article>
              )
            })}
          </div>
        </div>
      </section>

      <section className="bg-slate-50 py-24 dark:bg-slate-900">
        <div className="mx-auto max-w-7xl px-5 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
              Designed for operational clarity
            </p>

            <h2 className="mt-4 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
              See the network problem, not just the alarms.
            </h2>

            <p className="mt-5 text-lg leading-8 text-slate-600 dark:text-slate-300">
              Several degraded towers may be symptoms of one shared
              infrastructure fault.
            </p>
          </div>

          <div className="mx-auto mt-12 grid max-w-5xl items-stretch gap-6 lg:grid-cols-[1fr_auto_1fr] lg:items-center">
            <article className="rounded-3xl border border-red-200 bg-white p-7 shadow-sm dark:border-red-900/60 dark:bg-slate-950">
              <p className="text-sm font-bold uppercase tracking-[0.16em] text-red-600 dark:text-red-400">
                Without correlation
              </p>

              <div className="mt-6 space-y-3">
                {scatteredAlerts.map((alert) => (
                  <div
                    key={alert}
                    className="flex items-center gap-3 rounded-xl border border-red-100 bg-red-50 p-4 text-sm font-semibold text-slate-700 dark:border-red-900/50 dark:bg-red-950/30 dark:text-slate-200"
                  >
                    <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
                    {alert}
                  </div>
                ))}
              </div>
            </article>

            <ArrowRight
              className="mx-auto rotate-90 text-blue-600 lg:rotate-0 dark:text-blue-400"
              size={32}
              aria-hidden="true"
            />

            <article className="flex h-full flex-col justify-center rounded-3xl border border-blue-200 bg-blue-50 p-7 shadow-sm dark:border-blue-900/60 dark:bg-blue-950/30">
              <div className="w-fit rounded-xl bg-blue-600 p-3 text-white">
                <Network size={25} aria-hidden="true" />
              </div>

              <p className="mt-6 text-sm font-bold uppercase tracking-[0.16em] text-blue-700 dark:text-blue-300">
                With NetSage
              </p>

              <h3 className="mt-3 text-2xl font-black text-slate-950 dark:text-white">
                One probable shared uplink incident
              </h3>

              <p className="mt-3 leading-7 text-slate-600 dark:text-slate-300">
                Correlated evidence connects three affected towers to a shared
                dependency, giving engineers one operational context to
                investigate.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section className="bg-white py-24 dark:bg-slate-950">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 lg:grid-cols-2 lg:px-8">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
              Customer impact
            </p>

            <h2 className="mt-4 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
              Operational visibility should improve customer communication too.
            </h2>

            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              Incident context helps operations teams send timely, factual
              outage updates instead of generic messages.
            </p>
          </div>

          <article className="rounded-3xl border border-slate-200 bg-slate-50 p-7 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-blue-100 p-3 text-blue-600 dark:bg-blue-950 dark:text-blue-300">
                <MessageSquareText size={24} aria-hidden="true" />
              </div>

              <div>
                <p className="font-bold text-slate-950 dark:text-white">
                  Customer outage update
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  SMS notification
                </p>
              </div>
            </div>

            <div className="mt-6 rounded-2xl bg-white p-5 text-sm leading-6 text-slate-600 dark:bg-slate-950 dark:text-slate-300">
              We are investigating a network incident affecting service in
              selected sites. Our operations team is working on recovery and
              will share another update when service is stable.
            </div>

            <p className="mt-4 text-xs text-slate-500 dark:text-slate-400">
              Messages are controlled by the operations workflow and delivery
              state can be tracked.
            </p>
          </article>
        </div>
      </section>

      <section
        id="demo"
        className="scroll-mt-24 bg-slate-950 py-24 text-white"
      >
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 lg:grid-cols-2 lg:px-8">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-400">
              Live product experience
            </p>

            <h2 className="mt-4 text-4xl font-black tracking-tight">
              See NetSage in action
            </h2>

            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
              Explore the existing operations experience to review network
              health, alerts, topology and incident response.
            </p>

            <Link
              to="/operations"
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 font-semibold text-white transition hover:bg-blue-500"
            >
              Open Operations Demo
              <ArrowRight size={18} aria-hidden="true" />
            </Link>
          </div>

          <img
            src="/images/netsage-network-operations.png"
            alt="Preview of the NetSage network operations dashboard"
            className="w-full rounded-3xl border border-white/10 shadow-2xl"
          />
        </div>
      </section>
    </>
  )
}