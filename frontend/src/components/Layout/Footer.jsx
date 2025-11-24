import { Shield, Github, Twitter, Mail, ExternalLink, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gradient-to-b from-slate-900 to-slate-950 border-t border-slate-700/50 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Shield className="w-8 h-8 text-primary-400" />
              <span className="text-xl font-bold text-white">RugPull Detector</span>
            </div>
            <p className="text-slate-400 text-sm">
              AI-powered DeFi security analysis to protect your crypto investments from scams and rug pulls.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-slate-400 hover:text-primary-400 transition-colors text-sm">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/history" className="text-slate-400 hover:text-primary-400 transition-colors text-sm">
                  Analysis History
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-slate-400 hover:text-primary-400 transition-colors text-sm">
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-white font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-slate-400 hover:text-primary-400 transition-colors text-sm flex items-center">
                  Documentation <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-400 hover:text-primary-400 transition-colors text-sm flex items-center">
                  API Access <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-400 hover:text-primary-400 transition-colors text-sm flex items-center">
                  GitHub <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
            </ul>
          </div>

          {/* Connect */}
          <div>
            <h3 className="text-white font-semibold mb-4">Connect</h3>
            <div className="flex space-x-4">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer"
                 className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-primary-400 hover:bg-slate-700 transition-all">
                <Github className="w-5 h-5" />
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer"
                 className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-primary-400 hover:bg-slate-700 transition-all">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="mailto:contact@rugpulldetector.com"
                 className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-primary-400 hover:bg-slate-700 transition-all">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="border-t border-slate-800 pt-8 space-y-4">
          <div className="flex items-start space-x-2 text-yellow-500/80 bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-4">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm">
              <strong>Disclaimer:</strong> This tool is for informational purposes only and does not constitute financial advice. 
              Always conduct your own research (DYOR) before making any investment decisions.
            </p>
          </div>
          
          <p className="text-center text-slate-500 text-sm">
            © {currentYear} RugPull Detector. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
