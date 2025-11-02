import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'red' | 'yellow' | 'green' | 'blue';
}

export default function KPICard({ title, value, icon: Icon, trend, color = 'blue' }: KPICardProps) {
  const colorClasses = {
    red: 'bg-red-500/10 text-red-400 border-red-500/20',
    yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    green: 'bg-green-500/10 text-green-400 border-green-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  };

  return (
    <div className={`p-6 rounded-lg border ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <Icon className="h-10 w-10 opacity-50" />
      </div>
      {trend && (
        <div className="mt-2 text-xs text-gray-500">
          {trend === 'up' && '↑ Increasing'}
          {trend === 'down' && '↓ Decreasing'}
          {trend === 'neutral' && '→ Stable'}
        </div>
      )}
    </div>
  );
}



