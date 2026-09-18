import { ArrowRight, Network } from 'lucide-react'
import { Link } from 'react-router-dom'

const workflowSteps = [
  {
    number: '01',
    title: 'Monitor',
    description:
      'Observe network sites, devices and service-health signals.',
  },
  {
    number: '02',
    title: 'Detect',
    description:
      'Identify sustained faults and correlate related alerts.',
  },
  {
    number: '03',
    title: 'Respond',
    description:
      'Coordinate recovery and keep affected customers informed.',
  },
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
              Monitor. Detect. Respond.
            </h2>
          </div>

          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {workflowSteps.map((step) => (
              <article key={step.title}>
                <span className="text-sm font-black text-blue-600 dark:text-blue-400">
                  {step.number}
                </span>

                <h3 className="mt-4 text-2xl font-bold text-slate-950 dark:text-white">
                  {step.title}
                </h3>

                <p className="mt-3 leading-7 text-slate-600 dark:text-slate-300">
                  {step.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section
        id="demo"
        className="scroll-mt-24 bg-slate-950 py-24 text-white"
      >
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 lg:grid-cols-2 lg:px-8">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-blue-400">
              Product preview
            </p>

            <h2 className="mt-4 text-4xl font-black tracking-tight">
              See the network operations experience.
            </h2>

            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
              Explore the working NetSage dashboard used to monitor network
              health, review alerts and coordinate incident response.
            </p>

            <Link
              to="/operations"
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 font-semibold text-white transition hover:bg-blue-500"
            >
              Enter product demo
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

      <section className="bg-white py-24 dark:bg-slate-950">
        <div className="mx-auto max-w-5xl px-5 text-center">
          <Network
            className="mx-auto text-blue-600 dark:text-blue-400"
            size={38}
            aria-hidden="true"
          />

          <p className="mt-6 text-sm font-bold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
            Operational value
          </p>

          <h2 className="mt-4 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
            Clearer operations. Faster coordination. Better communication.
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
            Give network teams the visibility and context they need to respond
            confidently across the communities they serve.
          </p>

          <Link
            to="/operations"
            className="mt-8 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 font-semibold text-white transition hover:bg-blue-700"
          >
            View the NetSage demo
            <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
      </section>
    </>
  )
}