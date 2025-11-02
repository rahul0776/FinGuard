import { useState, useEffect, useCallback } from 'react';
import { Activity, AlertTriangle, Zap, TrendingUp } from 'lucide-react';
import KPICard from '../components/KPICard';
import AlertCard from '../components/AlertCard';
import { Alert, KPIMetrics } from '../types';
import { getAlerts, getMetrics } from '../utils/api';
import { useWebSocket } from '../hooks/useWebSocket';

export default function Dashboard() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [metrics, setMetrics] = useState<KPIMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  const handleNewAlert = useCallback((alert: Alert) => {
    console.log('New alert received:', alert);
    setAlerts((prev) => [alert, ...prev].slice(0, 50)); // Keep last 50
    
    // Show toast notification for high-risk alerts
    if (alert.risk_level === 'HIGH' || alert.risk_level === 'CRITICAL') {
      // You can integrate a toast library here
      console.log('🚨 High-risk alert:', alert.alert_id);
    }
  }, []);

  const { connected } = useWebSocket(handleNewAlert);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [alertsData, metricsData] = await Promise.all([
          getAlerts(1, 50),
          getMetrics(),
        ]);
        setAlerts(alertsData.alerts);
        setMetrics(metricsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Real-Time Fraud Detection</h1>
        <p className="text-gray-400 mt-2">
          Monitor transactions and detect fraudulent activity in real-time
        </p>
        <div className="mt-2 flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
          <span className="text-sm text-gray-400">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* KPIs */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Total Transactions"
            value={metrics.total_transactions.toLocaleString()}
            icon={Activity}
            color="blue"
          />
          <KPICard
            title="Total Alerts"
            value={metrics.total_alerts}
            icon={AlertTriangle}
            color="red"
          />
          <KPICard
            title="Alert Rate"
            value={`${metrics.alert_rate.toFixed(2)}%`}
            icon={TrendingUp}
            color="yellow"
          />
          <KPICard
            title="Avg Latency"
            value={`${metrics.avg_latency_ms.toFixed(0)}ms`}
            icon={Zap}
            color="green"
          />
        </div>
      )}

      {/* Alerts List */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Recent Alerts</h2>
          <span className="text-sm text-gray-400">{alerts.length} alerts</span>
        </div>

        {alerts.length === 0 ? (
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No alerts yet</p>
            <p className="text-sm text-gray-500 mt-2">
              Alerts will appear here when fraud is detected
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <AlertCard key={alert.alert_id} alert={alert} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}



