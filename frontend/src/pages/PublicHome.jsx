import { useEffect, useState } from 'react'
import Footer from '../components/marketing/Footer'
import Hero from '../components/marketing/Hero'
import Navbar from '../components/marketing/Navbar'
import ProblemIntro from '../components/marketing/ProblemIntro'
import ProductExperience from '../components/marketing/ProductExperience'
import ProductOverview from '../components/marketing/ProductOverview'

export default function PublicHome() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('netsage-theme') === 'dark'
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem(
      'netsage-theme',
      darkMode ? 'dark' : 'light'
    )
  }, [darkMode])

  return (
    <div className="min-h-screen bg-white text-slate-950 dark:bg-slate-950 dark:text-white">
      <Navbar
        darkMode={darkMode}
        onToggleTheme={() => setDarkMode((value) => !value)}
      />

      <main>
        <Hero />
        <ProblemIntro />
        <ProductOverview />
        <ProductExperience />
      </main>

      <Footer />
    </div>
  )
}