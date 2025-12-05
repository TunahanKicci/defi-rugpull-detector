import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, AlertCircle } from 'lucide-react'

export default function Home() {
  const [address, setAddress] = useState('')
  const [chain, setChain] = useState('ethereum')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    // Basic validation
    if (!address || address.length !== 42 || !address.startsWith('0x')) {
      setError('Please enter a valid contract address (0x...)')
      return
    }

    // Navigate to analysis page
    navigate(`/analyze/${address}?chain=${chain}`)
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 pb-2 bg-gradient-to-r from-primary-400 to-blue-600 text-transparent bg-clip-text">
          🛡️ DeFi Rug Pull Detector
        </h1>
        <p className="text-xl text-slate-300 mb-2">
          AI-Powered Risk Analysis for Crypto Tokens
        </p>
        <p className="text-slate-400">
          Analyze smart contracts for potential scams, rug pulls, and security risks
        </p>
      </div>

      {/* Search Card */}
      <div className="card mb-12">
        <h2 className="text-2xl font-bold mb-6 text-center">Analyze a Token Contract</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Contract Address
            </label>
            <input
              type="text"
              className="input"
              placeholder="0x..."
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Blockchain Network
            </label>
            <select
              className="input"
              value={chain}
              onChange={(e) => setChain(e.target.value)}
            >
              <option value="ethereum">Ethereum</option>
              <option value="bsc">Binance Smart Chain</option>
              <option value="polygon">Polygon</option>
            </select>
          </div>

          {error && (
            <div className="flex items-center space-x-2 text-danger-400 bg-danger-900/20 p-3 rounded-lg">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <button type="submit" className="w-full btn btn-primary flex items-center justify-center space-x-2 py-4 text-lg">
            <Search className="w-5 h-5" />
            <span>Analyze Contract</span>
          </button>
        </form>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card">
          <div className="text-3xl mb-3">🔍</div>
          <h3 className="text-lg font-bold mb-2">Smart Contract Scan</h3>
          <p className="text-slate-400 text-sm">
            Deep analysis of contract bytecode and dangerous functions
          </p>
        </div>

        <div className="card">
          <div className="text-3xl mb-3">💧</div>
          <h3 className="text-lg font-bold mb-2">Liquidity Analysis</h3>
          <p className="text-slate-400 text-sm">
            Check LP lock status and liquidity pool health
          </p>
        </div>

        <div className="card">
          <div className="text-3xl mb-3">🤖</div>
          <h3 className="text-lg font-bold mb-2">AI Risk Scoring</h3>
          <p className="text-slate-400 text-sm">
            ML-powered risk assessment with explainable results
          </p>
        </div>
      </div>
    </div>
  )
}
