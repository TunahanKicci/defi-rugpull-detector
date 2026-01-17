import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Fallback content for production build
const fallbackContent = `
# 🛡️ DeFi Rug Pull Detector

**Enterprise-grade DeFi güvenlik platformu** - Yatırımcıları dolandırıcılıklara karşı koruyan, Açıklanabilir Yapay Zeka (XAI) ve Ensemble ML ile desteklenen gerçek zamanlı risk analiz sistemi.

## 🎯 Temel Özellikler

### 🔬 Analiz Modülleri
- **Contract Security** - Akıllı kontrat güvenlik analizi
- **Holder Analysis** - Token holder dağılımı analizi
- **Liquidity Pool** - Likidite havuzu durumu
- **Transfer Anomaly** - Anormal transfer tespiti
- **Pattern Matching** - Bilinen scam patternleri
- **Tokenomics** - Token ekonomisi analizi
- **Honeypot Simulator** - Gerçek alım-satım simülasyonu
- **Whale Detector AI** - ML-based whale manipülasyon tespiti

### 🧠 Açıklanabilir Yapay Zeka (XAI)
"Neden bu token riskli?" sorusunu cevaplayabilen ileri seviye açıklama sistemi

### 🤖 Ensemble ML Sistemi
4 farklı ML modeli (XGBoost, LightGBM, CatBoost, Deep Neural Network) kullanarak en yüksek doğruluk

## ⚡ Özellikleri

- 🔄 **Real-time Analysis** - 20-30 saniyede kapsamlı analiz
- 📊 **Multi-chain Support** - Ethereum, BSC, Polygon
- 🎨 **Modern UI** - Responsive React + Tailwind CSS
- 📈 **Data Visualization** - Radar chart, Bar chart, Pie chart
- 🚀 **Async Architecture** - Non-blocking I/O, yüksek performans
- 📝 **Comprehensive Logging** - Detaylı analiz kayıtları
- 🌐 **RESTful API** - FastAPI + Swagger documentation

## 📖 Daha Fazla Bilgi

Detaylı bilgi için GitHub repository'sini ziyaret edin veya API Documentation sayfasını kontrol edin.
`

export default function About() {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="card">
        <h1 className="text-3xl font-bold mb-6">About / README</h1>
        <p className="text-sm text-slate-400 mb-4">
          Bu içerik proje hakkında bilgi sağlar.
        </p>

        <div className="prose prose-invert prose-slate max-w-none
                        prose-headings:text-slate-100 
                        prose-h1:text-3xl prose-h1:font-bold prose-h1:mb-4 prose-h1:border-b prose-h1:border-slate-700 prose-h1:pb-3
                        prose-h2:text-2xl prose-h2:font-bold prose-h2:mt-8 prose-h2:mb-4 prose-h2:border-b prose-h2:border-slate-800 prose-h2:pb-2
                        prose-h3:text-xl prose-h3:font-semibold prose-h3:mt-6 prose-h3:mb-3
                        prose-p:text-slate-300 prose-p:leading-7 prose-p:mb-4
                        prose-a:text-blue-400 prose-a:no-underline hover:prose-a:text-blue-300 hover:prose-a:underline
                        prose-strong:text-slate-100 prose-strong:font-semibold
                        prose-code:text-emerald-400 prose-code:bg-slate-900/60 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
                        prose-pre:bg-slate-900/60 prose-pre:border prose-pre:border-slate-800 prose-pre:rounded-lg prose-pre:p-4
                        prose-blockquote:border-l-4 prose-blockquote:border-yellow-500/50 prose-blockquote:bg-yellow-500/5 prose-blockquote:pl-4 prose-blockquote:py-2 prose-blockquote:italic prose-blockquote:text-slate-300
                        prose-ul:text-slate-300 prose-ul:list-disc prose-ul:ml-6 prose-ul:mb-4
                        prose-ol:text-slate-300 prose-ol:list-decimal prose-ol:ml-6 prose-ol:mb-4
                        prose-li:mb-2
                        prose-table:border-collapse prose-table:w-full prose-table:mb-6
                        prose-thead:bg-slate-800/50 prose-thead:border-b-2 prose-thead:border-slate-700
                        prose-th:text-left prose-th:px-4 prose-th:py-3 prose-th:font-semibold prose-th:text-slate-200 prose-th:border prose-th:border-slate-700
                        prose-td:px-4 prose-td:py-3 prose-td:text-slate-300 prose-td:border prose-td:border-slate-800
                        prose-tr:border-b prose-tr:border-slate-800
                        prose-img:rounded-lg prose-img:shadow-lg
                        ">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {fallbackContent}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
