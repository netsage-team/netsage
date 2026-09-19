import { Menu, Moon, Sun, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'

const navigationItems = [
  { label: 'Home', href: '#home' },
  { label: 'Product', href: '#product' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'About', href: '#about' },
]

export default function Navbar({
  darkMode,
  onToggleTheme,
}) {
  const [menuOpen, setMenuOpen] = useState(false)

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
      <nav
        aria-label="Main navigation"
        className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8"
      >
        <a
          href="#home"
          className="flex items-center"
          aria-label="NetSage homepage"
        >
          <img
            src="/images/netsage-logo.png"
            alt="NetSage"
            className="h-9 w-auto"
          />
        </a>

        <div className="hidden items-center gap-7 md:flex">
          {navigationItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="text-sm font-semibold text-slate-600 transition hover:text-blue-600 dark:text-slate-300 dark:hover:text-blue-400"
            >
              {item.label}
            </a>
          ))}

          <button
            type="button"
            onClick={onToggleTheme}
            className="rounded-xl border border-slate-200 p-2.5 text-slate-600 transition hover:border-blue-300 hover:text-blue-600 dark:border-slate-700 dark:text-slate-300"
            aria-label={darkMode ? 'Use light mode' : 'Use dark mode'}
          >
            {darkMode ? <Sun size={19} /> : <Moon size={19} />}
          </button>

          <Link
            to="/operations"
            className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            View operations
          </Link>
        </div>

        <button
          type="button"
          className="rounded-lg border border-slate-200 p-2 md:hidden dark:border-slate-700"
          onClick={() => setMenuOpen((value) => !value)}
          aria-expanded={menuOpen}
          aria-controls="mobile-navigation"
          aria-label={menuOpen ? 'Close navigation' : 'Open navigation'}
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {menuOpen && (
        <div
          id="mobile-navigation"
          className="border-t border-slate-200 bg-white px-5 py-5 dark:border-slate-800 dark:bg-slate-950 md:hidden"
        >
          <div className="flex flex-col gap-4">
            {navigationItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={closeMenu}
                className="font-semibold text-slate-700 dark:text-slate-200"
              >
                {item.label}
              </a>
            ))}

            <button
              type="button"
              onClick={onToggleTheme}
              className="flex items-center gap-2 font-semibold text-slate-700 dark:text-slate-200"
            >
              {darkMode ? <Sun size={19} /> : <Moon size={19} />}
              {darkMode ? 'Light mode' : 'Dark mode'}
            </button>

            <Link
              to="/operations"
              onClick={closeMenu}
              className="rounded-xl bg-blue-600 px-5 py-3 text-center font-semibold text-white"
            >
              View operations
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}