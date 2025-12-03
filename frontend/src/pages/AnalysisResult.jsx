import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { AlertTriangle, CheckCircle, XCircle, Loader, Shield, Users, Droplet, TrendingUp, Search, Coins } from 'lucide-react'
import { analyzeToken } from '../services/analysisService'
import { 
  RadarChart, 
  Radar, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

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
        
        // DEBUG: Log honeypot simulation data
        console.log('🔍 API Response:', data)
        console.log('🎯 Honeypot Simulation:', data?.honeypot_simulation)
        
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

  // Prepare radar chart data
  const getRadarData = () => {
    if (!result?.modules) return []
    
    return Object.entries(result.modules).map(([moduleName, moduleData]) => ({
      module: moduleName.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      score: 100 - moduleData.risk_score, // Inverted so higher is better
      risk: moduleData.risk_score
    }))
  }

  // Prepare holder distribution data
  const getHolderDistributionData = () => {
    const holderData = result?.modules?.holder_analysis?.data
    if (!holderData) return null

    const top10Percentage = holderData.top_10_holders_percentage || 0
    const othersPercentage = 100 - top10Percentage

    return [
      { name: 'Top 10 Holders', value: top10Percentage, color: '#ef4444' },
      { name: 'Other Holders', value: othersPercentage, color: '#22c55e' }
    ]
  }

  // Prepare top holders bar chart data
  const getTopHoldersData = () => {
    const holderData = result?.modules?.holder_analysis?.data
    if (!holderData?.top_holders) return []

    return holderData.top_holders.slice(0, 5).map((holder, idx) => ({
      name: `Holder ${idx + 1}`,
      address: holder.address ? `${holder.address.slice(0, 6)}...${holder.address.slice(-4)}` : `#${idx + 1}`,
      percentage: holder.percentage || 0
    }))
  }

  // Custom tooltip for radar chart
  const CustomRadarTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
          <p className="text-white font-semibold">{payload[0].payload.module}</p>
          <p className="text-green-400">Safety: {payload[0].value.toFixed(1)}</p>
          <p className="text-red-400">Risk: {payload[0].payload.risk.toFixed(1)}</p>
        </div>
      )
    }
    return null
  }

  // Custom tooltip for pie chart
  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
          <p className="text-white font-semibold">{payload[0].name}</p>
          <p className="text-primary-400">{payload[0].value.toFixed(2)}%</p>
        </div>
      )
    }
    return null
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
      {/* Radar Chart - Most Important */}
      <div className="card bg-gradient-to-br from-slate-900/90 to-slate-800/90 border-slate-700">
        <h2 className="text-2xl font-bold mb-6 text-center">Security Overview - Risk Analysis</h2>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={getRadarData()}>
            <PolarGrid stroke="#475569" />
            <PolarAngleAxis 
              dataKey="module" 
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              stroke="#475569"
            />
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 100]}
              tick={{ fill: '#64748b' }}
              stroke="#475569"
            />
            <Radar 
              name="Safety Score" 
              dataKey="score" 
              stroke="#22c55e" 
              fill="#22c55e" 
              fillOpacity={0.6}
              strokeWidth={2}
            />
            <Tooltip content={<CustomRadarTooltip />} />
            <Legend 
              wrapperStyle={{ color: '#94a3b8' }}
              formatter={(value) => <span className="text-slate-300">{value}</span>}
            />
          </RadarChart>
        </ResponsiveContainer>
        <p className="text-center text-sm text-slate-400 mt-4">
          Larger area indicates better security. Red zones show high-risk modules.
        </p>
      </div>

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

      {/* Honeypot Simulation - SPECIAL CARD */}
      {result.honeypot_simulation && (
        <div className={`card border-2 ${
          result.honeypot_simulation.data?.verdict === 'HONEYPOT' 
            ? 'border-red-500 bg-gradient-to-br from-red-900/20 to-red-800/10' 
            : result.honeypot_simulation.data?.verdict === 'SAFE'
            ? 'border-green-500 bg-gradient-to-br from-green-900/20 to-green-800/10'
            : 'border-yellow-500 bg-gradient-to-br from-yellow-900/20 to-yellow-800/10'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`p-3 rounded-lg ${
                result.honeypot_simulation.data?.verdict === 'HONEYPOT' 
                  ? 'bg-red-500/30' 
                  : result.honeypot_simulation.data?.verdict === 'SAFE'
                  ? 'bg-green-500/30'
                  : 'bg-yellow-500/30'
              }`}>
                <Shield className={`w-6 h-6 ${
                  result.honeypot_simulation.data?.verdict === 'HONEYPOT' 
                    ? 'text-red-400' 
                    : result.honeypot_simulation.data?.verdict === 'SAFE'
                    ? 'text-green-400'
                    : 'text-yellow-400'
                }`} />
              </div>
              <div>
                <h3 className="text-xl font-bold">🎯 Honeypot Simulation</h3>
                <p className="text-sm text-slate-400">Dynamic buy/sell transaction test</p>
              </div>
            </div>
            <div className={`px-4 py-2 rounded-lg font-bold text-lg ${
              result.honeypot_simulation.data?.verdict === 'HONEYPOT' 
                ? 'bg-red-500/30 text-red-300' 
                : result.honeypot_simulation.data?.verdict === 'SAFE'
                ? 'bg-green-500/30 text-green-300'
                : result.honeypot_simulation.data?.verdict === 'LOCKED'
                ? 'bg-red-500/30 text-red-300'
                : 'bg-yellow-500/30 text-yellow-300'
            }`}>
              {result.honeypot_simulation.data?.verdict || 'UNKNOWN'}
            </div>
          </div>

          {/* Simulation Results Grid */}
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            {/* Buy Simulation */}
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-400">Buy Test</span>
                {result.honeypot_simulation.data?.buy_simulation?.success ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-400" />
                )}
              </div>
              <p className="text-xs text-slate-300">
                {result.honeypot_simulation.data?.buy_simulation?.message || 'No data'}
              </p>
              {result.honeypot_simulation.data?.buy_simulation?.gas_estimate && (
                <p className="text-xs text-slate-500 mt-1">
                  Gas: {result.honeypot_simulation.data.buy_simulation.gas_estimate.toLocaleString()}
                </p>
              )}
            </div>

            {/* Sell Simulation */}
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-400">Sell Test</span>
                {result.honeypot_simulation.data?.sell_simulation?.success ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-400" />
                )}
              </div>
              <p className="text-xs text-slate-300">
                {result.honeypot_simulation.data?.sell_simulation?.message || 'No data'}
              </p>
              {result.honeypot_simulation.data?.sell_simulation?.gas_estimate && (
                <p className="text-xs text-slate-500 mt-1">
                  Gas: {result.honeypot_simulation.data.sell_simulation.gas_estimate.toLocaleString()}
                </p>
              )}
            </div>

            {/* Transfer Test */}
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-400">Transfer Test</span>
                {result.honeypot_simulation.data?.transfer_simulation ? (
                  result.honeypot_simulation.data.transfer_simulation.success ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )
                ) : (
                  <span className="text-xs text-slate-500">N/A</span>
                )}
              </div>
              <p className="text-xs text-slate-300">
                {result.honeypot_simulation.data?.transfer_simulation?.message || 'Not tested'}
              </p>
            </div>
          </div>

          {/* Warnings */}
          {result.honeypot_simulation.warnings && result.honeypot_simulation.warnings.length > 0 && (
            <div className="space-y-1">
              {result.honeypot_simulation.warnings.map((warning, idx) => (
                <div key={idx} className="flex items-start space-x-2 text-sm">
                  <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300">{warning}</span>
                </div>
              ))}
            </div>
          )}

          {/* Confidence */}
          <div className="mt-4 pt-4 border-t border-slate-700/50 text-sm text-slate-400">
            Confidence: <span className="font-semibold text-slate-300">
              {result.honeypot_simulation.data?.verdict_confidence || 'unknown'}
            </span>
          </div>
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
          
          // Special rendering for holder_analysis with charts
          if (moduleName === 'holder_analysis') {
            const holderDistribution = getHolderDistributionData()
            const topHoldersData = getTopHoldersData()
            
            return (
              <div 
                key={moduleName} 
                className={`card bg-gradient-to-br ${bgGradient} border-slate-700/50 hover:border-slate-600 transition-all duration-300 md:col-span-2`}
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
                  <span className={`text-2xl font-bold ${getRiskColor(score)}`}>
                    {score.toFixed(0)}
                  </span>
                </div>

                {/* Charts Row */}
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  {/* Pie Chart - Holder Distribution */}
                  {holderDistribution && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-300 mb-2 text-center">
                        Token Distribution
                      </h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                          <Pie
                            data={holderDistribution}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                            outerRadius={70}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {holderDistribution.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip content={<CustomPieTooltip />} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {/* Bar Chart - Top Holders */}
                  {topHoldersData.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-300 mb-2 text-center">
                        Top 5 Holders
                      </h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart 
                          data={topHoldersData}
                          layout="horizontal"
                          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                          <XAxis type="number" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                          <YAxis 
                            type="category" 
                            dataKey="address" 
                            stroke="#64748b" 
                            tick={{ fill: '#94a3b8', fontSize: 9 }}
                            width={70}
                          />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1e293b', 
                              border: '1px solid #475569',
                              borderRadius: '0.5rem',
                              color: '#e2e8f0'
                            }}
                          />
                          <Bar dataKey="percentage" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>

                {/* Metrics */}
                {moduleData.data && (
                  <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-slate-800/40 rounded-lg">
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Gini Coefficient</p>
                      <p className="text-lg font-bold text-yellow-400">
                        {moduleData.data.gini_coefficient?.toFixed(3) || 'N/A'}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Total Holders</p>
                      <p className="text-lg font-bold text-blue-400">
                        {moduleData.data.total_holders || 'N/A'}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Top 10 Holdings</p>
                      <p className="text-lg font-bold text-red-400">
                        {moduleData.data.top_10_holders_percentage?.toFixed(1) || 'N/A'}%
                      </p>
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {moduleData.warnings && moduleData.warnings.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-slate-300">Key Findings:</p>
                    <ul className="space-y-1.5">
                      {moduleData.warnings.map((warning, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-xs text-slate-400">
                          <span className="text-slate-500">•</span>
                          <span>{warning}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )
          }

          // Special rendering for liquidity_pool with visualization
          if (moduleName === 'liquidity_pool') {
            const liquidityData = moduleData.data
            const liquidityMetrics = liquidityData ? [
              { name: 'Liquidity', value: parseFloat(liquidityData.liquidity_usd) || 0, color: '#3b82f6' },
              { name: 'Volume 24h', value: parseFloat(liquidityData.volume_24h) || 0, color: '#8b5cf6' },
            ].filter(m => m.value > 0) : []

            return (
              <div 
                key={moduleName} 
                className={`card bg-gradient-to-br ${bgGradient} border-slate-700/50 hover:border-slate-600 transition-all duration-300 md:col-span-2`}
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
                  <span className={`text-2xl font-bold ${getRiskColor(score)}`}>
                    {score.toFixed(0)}
                  </span>
                </div>

                {/* Liquidity Bar Chart */}
                {liquidityMetrics.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-slate-300 mb-2 text-center">
                      Liquidity Metrics
                    </h4>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={liquidityMetrics}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#94a3b8' }} />
                        <YAxis 
                          stroke="#64748b" 
                          tick={{ fill: '#94a3b8' }}
                          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
                        />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#1e293b', 
                            border: '1px solid #475569',
                            borderRadius: '0.5rem',
                            color: '#e2e8f0'
                          }}
                          formatter={(value) => [`$${value.toLocaleString()}`, 'Value']}
                        />
                        <Bar dataKey="value" fill="#3b82f6">
                          {liquidityMetrics.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Liquidity Metrics */}
                {liquidityData && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 p-3 bg-slate-800/40 rounded-lg">
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Liquidity USD</p>
                      <p className="text-sm font-bold text-blue-400">
                        ${parseFloat(liquidityData.liquidity_usd || 0).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Lock Status</p>
                      <p className={`text-sm font-bold ${liquidityData.is_locked ? 'text-green-400' : 'text-red-400'}`}>
                        {liquidityData.is_locked ? 'Locked' : 'Unlocked'}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Price USD</p>
                      <p className="text-sm font-bold text-purple-400">
                        ${parseFloat(liquidityData.price_usd || 0).toFixed(6)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Market Cap</p>
                      <p className="text-sm font-bold text-yellow-400">
                        ${parseFloat(liquidityData.market_cap || 0).toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {moduleData.warnings && moduleData.warnings.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-slate-300">Key Findings:</p>
                    <ul className="space-y-1.5">
                      {moduleData.warnings.map((warning, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-xs text-slate-400">
                          <span className="text-slate-500">•</span>
                          <span>{warning}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )
          }
          
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
