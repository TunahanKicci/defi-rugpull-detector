import { Link, useLocation } from 'react-router-dom'
import { Shield, Menu, X, Github, Twitter } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  const isActive = (path) => {
    return location.pathname === path 
      ? 'text-primary-400 border-b-2 border-primary-400' 
      : 'text-slate-300 hover:text-white border-b-2 border-transparent hover:border-slate-600'
  }

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/history', label: 'History' },
    { path: '/about', label: 'About' },
  ]

  return (
    <header className="sticky top-0 z-50 backdrop-blur-lg bg-slate-900/80 border-b border-slate-700/50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-primary-500/20 rounded-lg blur-md group-hover:blur-lg transition-all" />
              <Shield className="w-10 h-10 text-primary-400 relative z-10 group-hover:scale-110 transition-transform" />
            </div>
            <div>
              <span className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-blue-400 bg-clip-text text-transparent">
                RugPull Detector
              </span>
              <p className="text-xs text-slate-400">Protect Your DeFi</p>
            </div>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map(link => (
              <Link 
                key={link.path}
                to={link.path} 
                className={`px-4 py-2 transition-all ${isActive(link.path)}`}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Social Links */}
          <div className="hidden md:flex items-center space-x-4">
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" 
               className="text-slate-400 hover:text-primary-400 transition-colors">
              <Github className="w-5 h-5" />
            </a>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer"
               className="text-slate-400 hover:text-primary-400 transition-colors">
              <Twitter className="w-5 h-5" />
            </a>
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden p-2 text-slate-300 hover:text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-2 animate-fadeIn">
            {navLinks.map(link => (
              <Link 
                key={link.path}
                to={link.path} 
                className={`block px-4 py-2 rounded-lg transition-colors ${isActive(link.path)}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </header>
  )
}
