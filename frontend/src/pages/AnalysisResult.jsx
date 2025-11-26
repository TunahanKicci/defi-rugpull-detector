import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { AlertTriangle, CheckCircle, XCircle, Loader, Shield, Users, Droplet, TrendingUp, Search, Coins } from 'lucide-react'
import { analyzeToken } from '../services/analysisService'

// Module icons mapping
const moduleIcons = {
  contract_security: Shield,
  holder_analysis: Users,
  liquidity_pool: Droplet,
  transfer_anomaly: TrendingUp,
  pattern_matching: Search,
  tokenomics: Coins,
}

// Module descriptions
const moduleDescriptions = {
  contract_security: 'Smart contract bytecode and security analysis',
  holder_analysis: 'Token holder distribution and concentration',
  liquidity_pool: 'Liquidity depth and lock status',
  transfer_anomaly: 'Unusual transfer patterns and behaviors',
  pattern_matching: 'Known scam patterns and similarities',
  tokenomics: 'Token supply, taxes, and economics',
}

export default function AnalysisResult() {
  const { address } = useParams()
  const [searchParams] = useSearchParams()
  const chain = searchParams.get('chain') || 'ethereum'

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  useEffect(() => {
    let cancelled = false
    
    const fetchAnalysis = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await analyzeToken(address, chain)
        
        if (!cancelled) {
          setResult(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Failed to analyze token')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchAnalysis()
    
    return () => {
      cancelled = true
    }
  }, [address, chain])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader className="w-16 h-16 text-primary-500 animate-spin mx-auto mb-4" />
          <p className="text-xl text-slate-300">Analyzing contract...</p>
          <p className="text-slate-400 mt-2">This may take a few moments</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card bg-danger-900/20 border-danger-700">
          <div className="flex items-center space-x-3 mb-4">
            <XCircle className="w-8 h-8 text-danger-500" />
            <h2 className="text-2xl font-bold text-danger-400">Analysis Failed</h2>
          </div>
          <p className="text-slate-300">{error}</p>
        </div>
      </div>
    )
  }

  const getRiskColor = (score) => {
    if (score >= 80) return 'text-danger-500'
    if (score >= 60) return 'text-orange-500'
    if (score >= 40) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getRiskBg = (score) => {
    if (score >= 80) return 'bg-danger-900/20 border-danger-700'
    if (score >= 60) return 'bg-orange-900/20 border-orange-700'
    if (score >= 40) return 'bg-yellow-900/20 border-yellow-700'
    return 'bg-green-900/20 border-green-700'
  }

  return (
    <div className="relative min-h-screen">
      {/* Animated Background Gradient */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div 
          className="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: '0s' }}
        />
        <div 
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: '1s' }}
        />
        <div 
          className="absolute top-1/2 left-1/2 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: '2s' }}
        />
      </div>

      <div className="max-w-6xl mx-auto space-y-6 relative z-10">
      {/* Risk Score Card */}
      <div className={`card ${getRiskBg(result.risk_score)}`}>
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Risk Assessment</h2>
          <div className={`text-7xl font-bold ${getRiskColor(result.risk_score)} mb-2`}>
            {result.risk_score.toFixed(1)}
          </div>
          <div className="text-2xl font-semibold mb-4">{result.risk_level}</div>
          <p className="text-slate-300">
            {result.contract_info?.symbol || 'Token'} • {result.chain}
          </p>
        </div>
      </div>

      {/* Red Flags */}
      {result.red_flags && result.red_flags.length > 0 && (
        <div className="card bg-danger-900/20 border-danger-700">
          <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
            <AlertTriangle className="w-6 h-6 text-danger-500" />
            <span>Critical Issues</span>
          </h3>
          <ul className="space-y-2">
            {result.red_flags.map((flag, idx) => (
              <li key={idx} className="flex items-start space-x-2 text-danger-300">
                <span>•</span>
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {result.recommendations && result.recommendations.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4">Recommendations</h3>
          <ul className="space-y-2">
            {result.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start space-x-2 text-slate-300">
                <span>•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Module Results */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(result.modules || {}).map(([moduleName, moduleData]) => {
          const Icon = moduleIcons[moduleName] || Shield
          const score = moduleData.risk_score
          const bgGradient = score >= 70 
            ? 'from-red-900/10 to-red-800/5' 
            : score >= 40 
            ? 'from-yellow-900/10 to-yellow-800/5'
            : 'from-green-900/10 to-green-800/5'
          
          return (
            <div 
              key={moduleName} 
              className={`card bg-gradient-to-br ${bgGradient} border-slate-700/50 hover:border-slate-600 transition-all duration-300 hover:scale-105`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${score >= 70 ? 'bg-red-500/20' : score >= 40 ? 'bg-yellow-500/20' : 'bg-green-500/20'}`}>
                    <Icon className={`w-5 h-5 ${getRiskColor(score)}`} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold capitalize">
                      {moduleName.replace(/_/g, ' ')}
                    </h3>
                    <p className="text-xs text-slate-400">
                      {moduleDescriptions[moduleName]}
                    </p>
                  </div>
                </div>
              </div>

              {/* Risk Score Bar */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-400">Risk Score</span>
                  <span className={`text-2xl font-bold ${getRiskColor(score)}`}>
                    {score.toFixed(0)}
                  </span>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${
                      score >= 70 ? 'bg-gradient-to-r from-red-500 to-red-600' : 
                      score >= 40 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' : 
                      'bg-gradient-to-r from-green-500 to-green-600'
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>

              {/* Warnings */}
              {moduleData.warnings && moduleData.warnings.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-slate-300">Key Findings:</p>
                  <ul className="space-y-1.5">
                    {moduleData.warnings.slice(0, 3).map((warning, idx) => (
                      <li key={idx} className="flex items-start space-x-2 text-xs text-slate-400">
                        <span className="text-slate-500">•</span>
                        <span className="line-clamp-2">{warning}</span>
                      </li>
                    ))}
                  </ul>
                  {moduleData.warnings.length > 3 && (
                    <p className="text-xs text-slate-500 mt-2">
                      +{moduleData.warnings.length - 3} more findings
                    </p>
                  )}
                </div>
              )}

              {/* Additional Data */}
              {moduleData.data && Object.keys(moduleData.data).length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-700/50">
                  <p className="text-xs font-semibold text-slate-300 mb-2">Additional Info:</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(moduleData.data).slice(0, 4).map(([key, value]) => {
                      if (typeof value === 'object' || key.includes('_')) return null
                      return (
                        <div key={key} className="truncate">
                          <span className="text-slate-500">{key}: </span>
                          <span className="text-slate-300">{String(value).substring(0, 20)}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
      </div>
    </div>
  )
}
