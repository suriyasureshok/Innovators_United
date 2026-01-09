import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MainLayout } from '@/components/layout/MainLayout';
import { alerts, behaviorPatterns, Alert } from '@/data/mockData';
import { cn } from '@/lib/utils';
import { AlertTriangle, CheckCircle, Clock, Building2, ChevronRight, Shield, Fingerprint, Network, Send } from 'lucide-react';

function AlertCard({ alert, isSelected, onClick }: { alert: Alert; isSelected: boolean; onClick: () => void }) {
  const pattern = behaviorPatterns.find(p => p.id === alert.patternId);

  return (
    <motion.div
      className={cn(
        'glass-card p-4 cursor-pointer transition-all',
        isSelected && 'ring-2 ring-primary',
        alert.intentLevel === 'escalated' && alert.status === 'active' && 'pulse-escalated'
      )}
      onClick={onClick}
      whileHover={{ scale: 1.01 }}
      layout
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className={cn(
            'w-4 h-4',
            alert.intentLevel === 'escalated' ? 'text-destructive' : 'text-warning'
          )} />
          <span className="font-mono text-sm font-medium text-foreground">{alert.id}</span>
        </div>
        <span className={cn(
          'text-xs font-medium px-2 py-0.5 rounded-full',
          alert.status === 'active' 
            ? 'bg-destructive/20 text-destructive' 
            : 'bg-success/20 text-success'
        )}>
          {alert.status}
        </span>
      </div>

      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg font-bold text-primary font-mono">{alert.patternId}</span>
        <span className={cn(
          'text-xs uppercase',
          alert.intentLevel === 'escalated' ? 'badge-escalated' : 'badge-elevated'
        )}>
          {alert.intentLevel}
        </span>
      </div>

      <p className="text-sm text-muted-foreground mb-3">{pattern?.description}</p>

      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {alert.timeWindow}
        </div>
        <div className="flex items-center gap-1">
          <Building2 className="w-3 h-3" />
          {alert.institutionCount} institutions
        </div>
      </div>
    </motion.div>
  );
}

function ExplainabilityPanel({ alert }: { alert: Alert | null }) {
  if (!alert) {
    return (
      <div className="glass-card p-6 h-full flex flex-col items-center justify-center text-center">
        <Shield className="w-12 h-12 text-muted-foreground mb-4" />
        <p className="text-sm text-muted-foreground">Select an alert to view<br />explainability chain</p>
      </div>
    );
  }

  const pattern = behaviorPatterns.find(p => p.id === alert.patternId);

  const explanationSteps = [
    {
      icon: Fingerprint,
      title: 'Local Behavior Pattern',
      description: `Pattern ${alert.patternId} detected by individual institutions`,
      detail: pattern?.description || '',
    },
    {
      icon: Network,
      title: 'Cross-Institution Correlation',
      description: `BRIDGE identified pattern across ${alert.institutionCount} institutions`,
      detail: `Time window: ${alert.timeWindow}`,
    },
    {
      icon: AlertTriangle,
      title: 'BRIDGE Intent Escalation',
      description: `Intent level escalated to "${alert.intentLevel}"`,
      detail: alert.triggerRule,
    },
    {
      icon: Send,
      title: 'Advisory Issued',
      description: 'Global intent advisory sent to participating institutions',
      detail: `Confidence score: ${(alert.confidenceScore * 100).toFixed(0)}%`,
    },
  ];

  return (
    <motion.div
      className="glass-card p-6 h-full overflow-auto"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex items-center gap-2 mb-6">
        <Shield className="w-5 h-5 text-primary" />
        <h3 className="section-title">Explainability Chain</h3>
      </div>

      {/* Alert Summary */}
      <div className={cn(
        'rounded-lg p-4 mb-6',
        alert.intentLevel === 'escalated' ? 'bg-destructive/10 border border-destructive/30' : 'bg-warning/10 border border-warning/30'
      )}>
        <div className="flex items-center justify-between mb-2">
          <span className="font-mono font-bold text-foreground">{alert.id}</span>
          <span className={alert.intentLevel === 'escalated' ? 'badge-escalated' : 'badge-elevated'}>
            {alert.intentLevel}
          </span>
        </div>
        <p className="text-sm text-muted-foreground">
          Pattern <span className="text-primary font-mono font-medium">{alert.patternId}</span> triggered alert at {new Date(alert.timestamp).toLocaleTimeString()}
        </p>
      </div>

      {/* Explanation Chain */}
      <div className="space-y-1 mb-6">
        {explanationSteps.map((step, index) => {
          const Icon = step.icon;
          return (
            <motion.div
              key={index}
              className="explanation-step explanation-step-active"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="flex items-start gap-3">
                <div className="p-1.5 rounded-lg bg-primary/10 mt-0.5">
                  <Icon className="w-3.5 h-3.5 text-primary" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground">{step.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>
                  <p className="text-xs text-primary mt-1 font-mono">{step.detail}</p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Metrics */}
      <div className="pt-4 border-t border-border">
        <p className="subsection-title mb-3">Alert Metrics</p>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-secondary/30 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Trigger Rule</p>
            <p className="text-xs text-foreground mt-1">{alert.triggerRule}</p>
          </div>
          <div className="bg-secondary/30 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Confidence</p>
            <p className="text-lg font-bold text-primary">{(alert.confidenceScore * 100).toFixed(0)}%</p>
          </div>
          <div className="bg-secondary/30 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Institutions</p>
            <p className="text-lg font-bold text-foreground">{alert.institutionCount}</p>
          </div>
          <div className="bg-secondary/30 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Time Window</p>
            <p className="text-sm font-medium text-foreground">{alert.timeWindow}</p>
          </div>
        </div>
      </div>

      {/* Privacy Note */}
      <div className="mt-6 pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground leading-relaxed">
          <strong className="text-foreground">Privacy Preserved:</strong> This alert was generated without exposing 
          individual identities or raw transaction data. All decisions remain local to institutions.
        </p>
      </div>
    </motion.div>
  );
}

export default function Alerts() {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  const filteredAlerts = filterStatus
    ? alerts.filter(a => a.status === filterStatus)
    : alerts;

  return (
    <MainLayout>
      <div className="space-y-6 h-full">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">Alerts & Explainability</h1>
            <p className="text-muted-foreground mt-1">Transparent reasoning behind every alert</p>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilterStatus(null)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                !filterStatus ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:bg-secondary/50'
              )}
            >
              All ({alerts.length})
            </button>
            <button
              onClick={() => setFilterStatus('active')}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                filterStatus === 'active' ? 'bg-destructive/20 text-destructive' : 'text-muted-foreground hover:bg-secondary/50'
              )}
            >
              Active ({alerts.filter(a => a.status === 'active').length})
            </button>
            <button
              onClick={() => setFilterStatus('reviewed')}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                filterStatus === 'reviewed' ? 'bg-success/20 text-success' : 'text-muted-foreground hover:bg-secondary/50'
              )}
            >
              Reviewed ({alerts.filter(a => a.status === 'reviewed').length})
            </button>
          </div>
        </motion.div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-220px)]">
          {/* Alert Feed */}
          <div className="space-y-4 overflow-auto pr-2">
            <AnimatePresence>
              {filteredAlerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  isSelected={selectedAlert?.id === alert.id}
                  onClick={() => setSelectedAlert(alert)}
                />
              ))}
            </AnimatePresence>
          </div>

          {/* Explainability Panel */}
          <ExplainabilityPanel alert={selectedAlert} />
        </div>
      </div>
    </MainLayout>
  );
}
