import {
  Activity,
  BellRing,
  GitMerge,
  MessageSquareText,
} from 'lucide-react'

const capabilities = [
  {
    title: 'Monitor network health',
    description:
      'Observe the condition of distributed sites, devices and connections.',
    icon: Activity,
  },
  {
    title: 'Detect degradation',
    description:
      'Identify sustained latency, packet loss and connectivity problems.',
    icon: BellRing,
  },
  {
    title: 'Understand incidents',
    description:
      'Correlate related alerts and identify the sites affected by a shared fault.',
    icon: GitMerge,
  },
  {
    title: 'Coordinate response',
    description:
      'Support recovery workflows and timely customer communication.',
    icon: MessageSquareText,
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
            NetSage gives internet service providers a connected operational
            view for moving from detection to investigation, response and
            customer communication.
          </p>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-2">
          {capabilities.map(({ title, description, icon: Icon }) => (
            <article
              key={title}
              className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm dark:border-slate-700 dark:bg-slate-950"
            >
              <div className="inline-flex rounded-xl bg-blue-50 p-3 text-blue-600 dark:bg-blue-950 dark:text-blue-300">
                <Icon size={24} aria-hidden="true" />
              </div>

              <h3 className="mt-6 text-xl font-bold text-slate-950 dark:text-white">
                {title}
              </h3>

              <p className="mt-3 leading-7 text-slate-600 dark:text-slate-300">
                {description}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}