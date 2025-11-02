import { Link } from 'react-router-dom';
import { AlertTriangle, ArrowRight } from 'lucide-react';
import { Alert } from '../types';

interface AlertCardProps {
  alert: Alert;
}

export default function AlertCard({ alert }: AlertCardProps) {
  const riskColors = {
    LOW: 'bg-green-500/10 text-green-400 border-green-500/20',
    MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/20',
  };

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-4 hover:border-slate-600 transition">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <AlertTriangle className={`h-6 w-6 mt-1 ${alert.risk_level === 'CRITICAL' || alert.risk_level === 'HIGH' ? 'text-red-500' : 'text-yellow-500'}`} />
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-white">{alert.alert_id}</h3>
              <span className={`px-2 py-1 text-xs rounded ${riskColors[alert.risk_level]}`}>
                {alert.risk_level}
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-1">
              {alert.merchant_name} • ${alert.amount.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Score: {(alert.score * 100).toFixed(1)}% • {alert.rules.length} rules triggered
            </p>
            <p className="text-xs text-gray-500">
              {new Date(alert.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
        <Link
          to={`/case/${alert.alert_id}`}
          className="flex items-center text-sm text-blue-400 hover:text-blue-300"
        >
          Details <ArrowRight className="h-4 w-4 ml-1" />
        </Link>
      </div>
    </div>
  );
}



