import { AlertTriangle, GitMerge } from 'lucide-react'

export default function ProblemIntro() {
  return (
    <section
      id="about"
      className="scroll-mt-24 bg-white py-24 dark:bg-slate-950"
    >
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-red-600 dark:text-red-400">
              The operational challenge
            </p>

            <h2 className="mt-4 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
              Network incidents rarely arrive as one clear alert.
            </h2>

            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              Distributed ISP infrastructure can produce alarms across several
              sites at once. Teams must determine whether they are seeing
              separate failures or symptoms of one shared network problem.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-[1fr_auto_1fr] sm:items-center">
            <div className="rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-900/60 dark:bg-red-950/30">
              <AlertTriangle
                className="text-red-600 dark:text-red-400"
                size={26}
                aria-hidden="true"
              />
              <p className="mt-4 font-bold text-slate-950 dark:text-white">
                Scattered alarms
              </p>
              <ul className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                <li>Tower A degradation</li>
                <li>Tower B packet loss</li>
                <li>Tower C latency alert</li>
              </ul>
            </div>

            <GitMerge
             className="mx-auto rotate-90 text-blue-600 sm:rotate-0 dark:text-blue-400"
              size={28}
              aria-hidden="true"
            />

            <div className="rounded-2xl border border-blue-200 bg-blue-50 p-6 dark:border-blue-900/60 dark:bg-blue-950/30">
              <GitMerge
                className="text-blue-600 dark:text-blue-400"
                size={26}
                aria-hidden="true"
              />
              <p className="mt-4 font-bold text-slate-950 dark:text-white">
                Correlated evidence
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
                One probable shared dependency affecting multiple sites.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}