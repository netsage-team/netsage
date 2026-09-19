import {
  Activity,
  AlertTriangle,
  GitMerge,
  MessageSquareText,
  Network,
} from 'lucide-react'

const demoSites = [
  {
    name: 'Mukono Central',
    metric: '184 ms latency',
  },
  {
    name: 'Seeta',
    metric: '7.2% packet loss',
  },
  {
    name: 'UCU Area',
    metric: '169 ms latency',
  },
]

export default function DemoPreview() {
  return (
    <div
      className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900 shadow-2xl"
      aria-label="NetSage Mukono incident demo preview"
    >
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
        <div>
          <p className="text-sm font-bold text-white">Mukono demo scenario</p>
          <p className="mt-1 text-xs text-slate-400">
            Clearly labelled demonstration data
          </p>
        </div>

        <span className="inline-flex items-center gap-2 rounded-full bg-red-500/15 px-3 py-1.5 text-xs font-bold text-red-300">
          <AlertTriangle size={14} aria-hidden="true" />
          Active incident
        </span>
      </div>

      <div className="p-5">
        <div className="grid gap-3 sm:grid-cols-3">
          {demoSites.map((site) => (
            <article
              key={site.name}
              className="rounded-2xl border border-red-400/20 bg-red-500/10 p-4"
            >
              <div className="flex items-center justify-between">
                <Activity
                  size={18}
                  className="text-red-300"
                  aria-hidden="true"
                />
                <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
              </div>

              <h3 className="mt-4 text-sm font-bold text-white">
                {site.name}
              </h3>

              <p className="mt-2 text-xs text-red-200">
                Sustained degradation
              </p>

              <p className="mt-1 text-xs text-slate-400">{site.metric}</p>
            </article>
          ))}
        </div>

        <div className="my-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-700" />
          <GitMerge
            size={20}
            className="text-blue-400"
            aria-hidden="true"
          />
          <div className="h-px flex-1 bg-slate-700" />
        </div>

        <article className="rounded-2xl border border-blue-400/30 bg-blue-500/10 p-5">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div className="flex items-start gap-3">
              <div className="rounded-xl bg-blue-500/15 p-2.5 text-blue-300">
                <Network size={21} aria-hidden="true" />
              </div>

              <div>
                <p className="text-xs font-bold uppercase tracking-[0.14em] text-blue-300">
                  Correlated evidence
                </p>
                <h3 className="mt-1 font-bold text-white">
                  Mukono Shared Uplink
                </h3>
                <p className="mt-1 text-xs text-slate-400">
                  Probable shared dependency affecting three sites
                </p>
              </div>
            </div>

            <span className="w-fit rounded-full bg-blue-400/15 px-3 py-1.5 text-xs font-semibold text-blue-200">
              3 sites affected
            </span>
          </div>
        </article>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-white/10 bg-slate-950/60 p-4">
            <p className="text-xs text-slate-400">Incident workflow</p>
            <p className="mt-1 text-sm font-semibold text-white">
              Investigation active
            </p>
          </div>

          <div className="rounded-xl border border-white/10 bg-slate-950/60 p-4">
            <div className="flex items-center gap-2 text-blue-300">
              <MessageSquareText size={16} aria-hidden="true" />
              <p className="text-xs">Customer communication</p>
            </div>
            <p className="mt-1 text-sm font-semibold text-white">
              Update ready for review
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}