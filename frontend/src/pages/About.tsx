import { Shield, Zap, Brain, Globe } from 'lucide-react';

export default function About() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-12">
        <Shield className="h-16 w-16 text-red-500 mx-auto mb-4" />
        <h1 className="text-4xl font-bold text-white mb-4">About FinGuard</h1>
        <p className="text-xl text-gray-400">
          Real-time fraud detection powered by rules-based scoring
        </p>
      </div>

      <div className="space-y-8">
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4">Architecture</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2 flex items-center">
                <Zap className="h-5 w-5 text-yellow-500 mr-2" />
                Backend
              </h3>
              <ul className="space-y-1 text-gray-400 text-sm">
                <li>• FastAPI on AWS Lambda</li>
                <li>• DynamoDB for hot path</li>
                <li>• S3 for cold storage</li>
                <li>• API Gateway (REST + WebSocket)</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2 flex items-center">
                <Brain className="h-5 w-5 text-purple-500 mr-2" />
                Rules Engine
              </h3>
              <ul className="space-y-1 text-gray-400 text-sm">
                <li>• Transaction velocity checks</li>
                <li>• Amount threshold detection</li>
                <li>• Geo-impossible travel detection</li>
                <li>• Device mismatch analysis</li>
                <li>• High-risk merchant categories</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4">Features</h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <Globe className="h-6 w-6 text-blue-500 mr-3 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-white font-semibold">Real-Time Scoring</h3>
                <p className="text-gray-400 text-sm">
                  Sub-150ms p95 latency for transaction scoring with rules-based detection
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <Brain className="h-6 w-6 text-purple-500 mr-3 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-white font-semibold">Explainable Detection</h3>
                <p className="text-gray-400 text-sm">
                  Feature contributions show why each transaction was flagged with clear explanations
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <Zap className="h-6 w-6 text-yellow-500 mr-3 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-white font-semibold">Live Dashboard</h3>
                <p className="text-gray-400 text-sm">
                  WebSocket-powered real-time alerts and KPI monitoring
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4">Cost & Performance</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-3xl font-bold text-green-400">$0</p>
              <p className="text-sm text-gray-400 mt-1">Monthly cost (Free Tier)</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-blue-400">&lt;150ms</p>
              <p className="text-sm text-gray-400 mt-1">p95 scoring latency</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4">Tech Stack</h2>
          <div className="flex flex-wrap gap-2">
            {['FastAPI', 'AWS Lambda', 'DynamoDB', 'S3', 'API Gateway', 'React', 'Vite', 'TypeScript', 'Tailwind', 'Recharts', 'Python 3.12'].map((tech) => (
              <span key={tech} className="px-3 py-1 bg-slate-700 text-gray-300 rounded-full text-sm">
                {tech}
              </span>
            ))}
          </div>
        </div>

        <div className="text-center text-gray-500 text-sm">
          <p>Built with ❤️ to demonstrate serverless fraud detection at scale</p>
          <p className="mt-2">MIT License • Open Source</p>
        </div>
      </div>
    </div>
  );
}



