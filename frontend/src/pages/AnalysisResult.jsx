import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { AlertTriangle, CheckCircle, XCircle, Loader } from 'lucide-react'
import { analyzeToken } from '../services/analysisService'

export default function AnalysisResult() {
  const { address } = useParams()
  const [searchParams] = useSearchParams()
  const chain = searchParams.get('chain') || 'ethereum'

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true)
        const data = await analyzeToken(address, chain)
        setResult(data)
      } catch (err) {
        setError(err.message || 'Failed to analyze token')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
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
    <div className="max-w-6xl mx-auto space-y-6">
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
      <div className="grid md:grid-cols-2 gap-6">
        {Object.entries(result.modules || {}).map(([moduleName, moduleData]) => (
          <div key={moduleName} className="card">
            <h3 className="text-lg font-bold mb-3 capitalize">
              {moduleName.replace(/_/g, ' ')}
            </h3>
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-slate-400">Risk Score</span>
                <span className={`font-bold ${getRiskColor(moduleData.risk_score)}`}>
                  {moduleData.risk_score.toFixed(1)}
                </span>
              </div>
            </div>
            {moduleData.warnings && moduleData.warnings.length > 0 && (
              <ul className="space-y-1 text-sm">
                {moduleData.warnings.slice(0, 3).map((warning, idx) => (
                  <li key={idx} className="text-slate-400">• {warning}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
