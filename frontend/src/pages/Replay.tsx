import { useState } from 'react';
import { Play, AlertCircle } from 'lucide-react';
import { triggerReplay } from '../utils/api';

export default function Replay() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleReplay = async () => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      
      const response = await triggerReplay('replay_day_01.csv', 1.0);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to trigger replay');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Transaction Replay</h1>
        <p className="text-gray-400 text-lg">
          Stream 5,000 synthetic transactions to see fraud detection in action
        </p>
      </div>

      <div className="bg-slate-800 rounded-lg border border-slate-700 p-8">
        <div className="text-center mb-8">
          <button
            onClick={handleReplay}
            disabled={loading}
            className="inline-flex items-center px-8 py-4 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white text-lg font-semibold rounded-lg transition"
          >
            <Play className="h-6 w-6 mr-3" />
            {loading ? 'Starting Replay...' : 'Replay Demo Day'}
          </button>
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-gray-400">Streaming transactions...</p>
            <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
          </div>
        )}

        {result && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-6">
            <h3 className="text-green-400 font-semibold text-lg mb-2">✓ Replay Started</h3>
            <p className="text-gray-300 mb-4">{result.message}</p>
            <p className="text-sm text-gray-400">
              Head to the <a href="/demo" className="text-blue-400 hover:underline">Live Demo</a> to see alerts in real-time
            </p>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6 flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-red-400 font-semibold mb-1">Error</h3>
              <p className="text-gray-300">{error}</p>
            </div>
          </div>
        )}

        <div className="mt-8 border-t border-slate-700 pt-6">
          <h3 className="text-white font-semibold mb-4">What happens during replay?</h3>
          <ul className="space-y-2 text-gray-400">
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">1.</span>
              5,000 synthetic transactions are streamed to the API
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">2.</span>
              Each transaction is scored for fraud in real-time
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">3.</span>
              High-risk transactions trigger alerts
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">4.</span>
              Alerts appear on the dashboard via WebSocket
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}



