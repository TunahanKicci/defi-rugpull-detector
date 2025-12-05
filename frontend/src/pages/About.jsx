import readmeContent from '../../../README.md?raw'

export default function About() {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="card">
        <h1 className="text-3xl font-bold mb-6">About / README</h1>
        <p className="text-sm text-slate-400 mb-4">
          Bu içerik doğrudan <code>README.md</code> dosyasından yüklenir; README güncellendikçe burası da yenilenir.
        </p>

        <pre className="whitespace-pre-wrap text-slate-100 text-sm leading-6 bg-slate-900/60 border border-slate-800 rounded-lg p-4 overflow-x-auto">
{readmeContent}
        </pre>
      </div>
    </div>
  )
}
