import {
  Activity,
  BellRing,
  CheckCircle2,
  GitMerge,
  History,
  Map,
  MessageSquareText,
  Workflow,
} from 'lucide-react'

const capabilities = [
  {
    title: 'Real-time monitoring',
    description:
      'Track latency, packet loss and service health across network devices.',
    icon: Activity,
  },
  {
    title: 'Degradation detection',
    description:
      'Identify sustained unhealthy conditions without treating every temporary spike as an incident.',
    icon: BellRing,
  },
  {
    title: 'Incident correlation',
    description:
      'Group related alerts and surface evidence of a probable shared dependency.',
    icon: GitMerge,
  },
  {
    title: 'Multi-site visibility',
    description:
      'See affected towers, sites and shared infrastructure in one operational context.',
    icon: Map,
  },
  {
    title: 'Incident operations',
    description:
      'Assign engineers, record investigation notes and follow the incident lifecycle.',
    icon: Workflow,
  },
  {
    title: 'Customer communication',
    description:
      'Send controlled outage updates through SMS and track delivery status.',
    icon: MessageSquareText,
  },
  {
    title: 'Recovery verification',
    description:
      'Confirm that healthy network conditions are sustained before resolution.',
    icon: CheckCircle2,
  },
  {
    title: 'Operational history',
    description:
      'Preserve incident activity, status changes and communication records for review.',
    icon: History,
  },
]

export default function ProductOverview() {
  return (
    <section
      id="product"
      className="scroll-mt-24 bg-slate-50 py-24 dark:bg-slate-900"
    >
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="max-w-3xl">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
            The NetSage solution
          </p>

          <h2 className="mt-4 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
            From network signals to coordinated action.
          </h2>

          <p className="mt-5 text-lg leading-8 text-slate-600 dark:text-slate-300">
            NetSage connects monitoring, incident context, engineering response
            and customer communication in one operational workflow.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {capabilities.map(({ title, description, icon: Icon }) => (
            <article
              key={title}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md dark:border-slate-700 dark:bg-slate-950"
            >
              <div className="inline-flex rounded-xl bg-blue-50 p-3 text-blue-600 dark:bg-blue-950 dark:text-blue-300">
                <Icon size={23} aria-hidden="true" />
              </div>

              <h3 className="mt-5 text-lg font-bold text-slate-950 dark:text-white">
                {title}
              </h3>

              <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
                {description}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}