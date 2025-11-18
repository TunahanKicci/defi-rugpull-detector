import { Link } from 'react-router-dom'
import { Shield } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50 backdrop-blur-sm bg-opacity-95">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 hover:opacity-80 transition">
            <Shield className="w-8 h-8 text-primary-500" />
            <div>
              <h1 className="text-2xl font-bold text-white">RugPull Detector</h1>
              <p className="text-xs text-slate-400">Protect Your DeFi Investments</p>
            </div>
          </Link>
          
          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/" className="text-slate-300 hover:text-white transition">
              Home
            </Link>
            <Link to="/history" className="text-slate-300 hover:text-white transition">
              History
            </Link>
            <Link to="/about" className="text-slate-300 hover:text-white transition">
              About
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
