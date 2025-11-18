export default function About() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <h1 className="text-3xl font-bold mb-6">About RugPull Detector</h1>
        
        <div className="space-y-6 text-slate-300">
          <p>
            DeFi Rug Pull Detector is an AI-powered tool designed to protect investors from 
            cryptocurrency scams and rug pulls. Using advanced machine learning and comprehensive 
            blockchain analysis, we provide risk assessments for token contracts.
          </p>

          <h2 className="text-2xl font-bold text-white mt-8 mb-4">Analysis Modules</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-bold text-white mb-2">🔒 Smart Contract Security</h3>
              <p className="text-sm">
                Scans contract bytecode for dangerous functions like mint, pause, and selfdestruct
              </p>
            </div>

            <div>
              <h3 className="font-bold text-white mb-2">📊 Holder Analysis</h3>
              <p className="text-sm">
                Analyzes token distribution and identifies excessive concentration
              </p>
            </div>

            <div>
              <h3 className="font-bold text-white mb-2">💧 Liquidity Pool Status</h3>
              <p className="text-sm">
                Checks if liquidity is locked and evaluates LP health
              </p>
            </div>

            <div>
              <h3 className="font-bold text-white mb-2">🔍 Transfer Anomalies</h3>
              <p className="text-sm">
                Detects unusual transfer patterns and whale movements
              </p>
            </div>

            <div>
              <h3 className="font-bold text-white mb-2">🎯 Scam Pattern Matching</h3>
              <p className="text-sm">
                Compares with known scam database and honeypot patterns
              </p>
            </div>

            <div>
              <h3 className="font-bold text-white mb-2">💰 Tokenomics Review</h3>
              <p className="text-sm">
                Analyzes buy/sell taxes and transaction limits
              </p>
            </div>

            <div>
              <h3 className="font-bold text-white mb-2">🤖 ML Risk Scoring</h3>
              <p className="text-sm">
                Combines all factors using machine learning for final risk assessment
              </p>
            </div>
          </div>

          <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4 mt-8">
            <p className="text-yellow-300 font-bold mb-2">⚠️ Disclaimer</p>
            <p className="text-sm text-yellow-200">
              This tool is for informational purposes only and does not constitute financial advice. 
              Always conduct your own research (DYOR) before investing in any cryptocurrency.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
