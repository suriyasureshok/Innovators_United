import { motion } from 'framer-motion';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KPICardProps {
  title: string;
  value: number | string;
  trend: string;
  icon: LucideIcon;
  variant?: 'default' | 'danger';
  onClick?: () => void;
}

export function KPICard({ title, value, trend, icon: Icon, variant = 'default', onClick }: KPICardProps) {
  const isPositiveTrend = trend.startsWith('+');
  const isDanger = variant === 'danger';

  return (
    <motion.div
      className={cn(
        'cursor-pointer transition-all duration-200',
        isDanger ? 'glass-card-danger pulse-escalated' : 'glass-card hover:glass-card-elevated'
      )}
      onClick={onClick}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className={cn(
            'p-2.5 rounded-lg',
            isDanger ? 'bg-destructive/20' : 'bg-primary/20'
          )}>
            <Icon className={cn(
              'w-5 h-5',
              isDanger ? 'text-destructive' : 'text-primary'
            )} />
          </div>
          <div className={cn(
            'flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full',
            isPositiveTrend 
              ? isDanger ? 'bg-destructive/10 text-destructive' : 'bg-success/10 text-success'
              : 'bg-success/10 text-success'
          )}>
            {isPositiveTrend ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {trend}
          </div>
        </div>
        <div className={isDanger ? 'kpi-value-danger' : 'kpi-value'}>
          {value}
        </div>
        <p className="text-sm text-muted-foreground mt-1">{title}</p>
      </div>
    </motion.div>
  );
}
