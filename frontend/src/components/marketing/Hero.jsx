import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Hero() {
  return (
    <section
      id="home"
      className="scroll-mt-24 overflow-hidden bg-slate-950 text-white"
    >
      <div className="mx-auto grid min-h-[720px] max-w-7xl items-center gap-14 px-5 py-20 lg:grid-cols-2 lg:px-8">
        <div>
          <p className="mb-6 text-sm font-semibold uppercase tracking-[0.22em] text-blue-400">
            Network monitoring and incident response
          </p>

          <h1 className="max-w-3xl text-5xl font-black leading-tight sm:text-6xl">
            Network clarity.
            <span className="block text-red-400">
              Connected communities.
            </span>
          </h1>

          <p className="mt-7 max-w-xl text-lg leading-8 text-slate-300">
            NetSage helps internet service providers monitor distributed
            network infrastructure, detect degradation, understand incidents
            and coordinate response.
          </p>

          <div className="mt-9 flex flex-col gap-4 sm:flex-row">
            <a
              href="#product"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 font-semibold text-white transition hover:bg-blue-500"
            >
              Explore NetSage
              <ArrowRight size={18} />
            </a>

            <Link
              to="/operations"
              className="inline-flex items-center justify-center rounded-xl border border-slate-600 px-6 py-3.5 font-semibold text-white transition hover:border-slate-400 hover:bg-white/5"
            >
              View operations demo
            </Link>
          </div>
        </div>

        <div className="relative" aria-label="NetSage network preview">
          <div className="absolute -inset-8 rounded-full bg-blue-600/20 blur-3xl" />

          <img
            src="/images/netsage-hero.png"
            alt="Connected network sites with one degraded location highlighted"
            className="relative w-full rounded-3xl border border-white/10 shadow-2xl"
          />
        </div>
      </div>
    </section>
  )
}