import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Alert } from '../types';
import { getAlert } from '../utils/api';

export default function AlertDetail() {
  const { alertId } = useParams<{ alertId: string }>();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlert = async () => {
      if (!alertId) return;
      
      try {
        setLoading(true);
        const data = await getAlert(alertId);
        setAlert(data);
      } catch (error) {
        console.error('Error fetching alert:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAlert();
  }, [alertId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading alert...</p>
        </div>
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Alert Not Found</h2>
          <p className="text-gray-400 mb-6">The alert you're looking for doesn't exist.</p>
          <Link to="/demo" className="text-blue-400 hover:text-blue-300">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const riskColors = {
    LOW: 'bg-green-500 text-white',
    MEDIUM: 'bg-yellow-500 text-white',
    HIGH: 'bg-orange-500 text-white',
    CRITICAL: 'bg-red-500 text-white',
  };

  // Prepare SHAP data for chart - sort by absolute contribution (descending)
  const shapData = alert.explanation.top_features
    .map(f => ({
      name: f.name.replace(/_/g, ' '),
      value: Math.abs(f.contribution),
      contribution: f.contribution,
      contribution_pct: f.contribution_pct,
    }))
    .sort((a, b) => b.value - a.value);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link to="/demo" className="text-blue-400 hover:text-blue-300 flex items-center mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to Dashboard
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white">{alert.alert_id}</h1>
          <p className="text-gray-400 mt-1">Fraud Alert Details</p>
        </div>
      </div>

      {/* Risk Score Card */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 rounded-lg p-8 mb-6 text-center">
        <div className="text-6xl font-bold mb-2">{(alert.score * 100).toFixed(1)}%</div>
        <div className="text-xl opacity-90 mb-4">Fraud Probability Score</div>
        <span className={`inline-block px-4 py-2 rounded-lg font-semibold ${riskColors[alert.risk_level]}`}>
          {alert.risk_level} RISK
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Transaction Details */}
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Transaction Details</h2>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-400">Transaction ID</p>
              <p className="text-white font-mono">{alert.txn_id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Card ID</p>
              <p className="text-white font-mono">{alert.card_id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Merchant</p>
              <p className="text-white">{alert.merchant_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Amount</p>
              <p className="text-white text-2xl font-bold">${alert.amount.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Timestamp</p>
              <p className="text-white">{new Date(alert.timestamp).toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Triggered Rules */}
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Triggered Rules</h2>
          {alert.rules.length > 0 ? (
            <ul className="space-y-2">
              {alert.rules.map((rule, idx) => (
                <li key={idx} className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-white">{rule.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400">No specific rules triggered. Detection based on ML model.</p>
          )}
        </div>
      </div>

      {/* Model Explanation */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 mb-6">
        <h2 className="text-xl font-bold text-white mb-4">Model Explanation</h2>
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-6">
          <p className="text-yellow-200">{alert.explanation.text}</p>
        </div>

        {/* SHAP Feature Contributions */}
        {shapData.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Feature Contributions</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={shapData} layout="horizontal" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  type="number" 
                  stroke="#9ca3af" 
                  domain={[0, 'dataMax']}
                  tickFormatter={(value) => value.toFixed(2)}
                />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  width={180} 
                  stroke="#9ca3af"
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#fff' }}
                  formatter={(value: number, name: string, props: any) => [
                    `${props.payload.contribution > 0 ? '+' : ''}${props.payload.contribution.toFixed(4)} (${props.payload.contribution_pct.toFixed(1)}%)`,
                    'Contribution'
                  ]}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} minPointSize={3}>
                  {shapData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.contribution > 0 ? '#ef4444' : '#10b981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* Feature Details Table */}
            <div className="mt-6 overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-300">Feature</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-300">Value</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-300">Contribution</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-300">Impact</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {alert.explanation.top_features.map((feature, idx) => (
                    <tr key={idx} className="hover:bg-slate-700/50">
                      <td className="px-4 py-2 text-white capitalize">
                        {feature.name.replace(/_/g, ' ')}
                      </td>
                      <td className="px-4 py-2 text-gray-300">{feature.value.toFixed(2)}</td>
                      <td className={`px-4 py-2 font-mono ${feature.contribution > 0 ? 'text-red-400' : 'text-green-400'}`}>
                        {feature.contribution > 0 ? '+' : ''}{feature.contribution.toFixed(4)}
                      </td>
                      <td className="px-4 py-2 text-gray-300">{feature.contribution_pct.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}



