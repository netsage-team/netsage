import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
      <div className="mx-auto grid max-w-7xl gap-8 px-5 py-10 md:grid-cols-3 lg:px-8">
        <div>
          <p className="font-bold text-slate-950 dark:text-white">NetSage</p>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Network clarity. Connected communities.
          </p>
        </div>

        <nav aria-label="Footer navigation" className="flex flex-col gap-3 text-sm">
          <a href="#home" className="text-slate-600 hover:text-blue-600 dark:text-slate-300">
            Home
          </a>
          <a href="#product" className="text-slate-600 hover:text-blue-600 dark:text-slate-300">
            Product
          </a>
          <a href="#how-it-works" className="text-slate-600 hover:text-blue-600 dark:text-slate-300">
            How It Works
          </a>
          <Link to="/operations" className="text-slate-600 hover:text-blue-600 dark:text-slate-300">
            Operations demo
          </Link>
        </nav>

        <div className="text-sm text-slate-500 dark:text-slate-400 md:text-right">
          <p>Built for the Connecting The Future Hackathon 2026.</p>
          <p className="mt-2">Uganda Christian University, Mukono.</p>
        </div>
      </div>
    </footer>
  )
}