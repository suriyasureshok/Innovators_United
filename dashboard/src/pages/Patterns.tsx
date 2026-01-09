import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MainLayout } from '@/components/layout/MainLayout';
import { behaviorPatterns, BehaviorPattern } from '@/data/mockData';
import { cn } from '@/lib/utils';
import { X, Clock, Building2, Activity, ChevronRight } from 'lucide-react';

function PatternCard({ pattern, onClick, isSelected }: { pattern: BehaviorPattern; onClick: () => void; isSelected: boolean }) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'escalated': return 'badge-escalated';
      case 'elevated': return 'badge-elevated';
      default: return 'badge-normal';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-destructive';
      case 'high': return 'text-warning';
      case 'medium': return 'text-primary';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <motion.div
      className={cn(
        'glass-card p-5 cursor-pointer transition-all',
        isSelected && 'ring-2 ring-primary',
        pattern.intentStatus === 'escalated' && 'pulse-escalated'
      )}
      onClick={onClick}
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
      layout
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-primary font-mono">{pattern.id}</span>
          <span className={getStatusBadge(pattern.intentStatus)}>
            {pattern.intentStatus}
          </span>
        </div>
        <span className={cn('text-xs font-medium uppercase', getSeverityColor(pattern.severityBucket))}>
          {pattern.severityBucket}
        </span>
      </div>

      <p className="text-sm text-foreground mb-4">{pattern.description}</p>

      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <Building2 className="w-3.5 h-3.5" />
          <span>{pattern.institutionCount} institutions</span>
        </div>
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <Activity className="w-3.5 h-3.5" />
          <span>{pattern.occurrences} occurrences</span>
        </div>
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <Clock className="w-3.5 h-3.5" />
          <span>{pattern.timeWindow}</span>
        </div>
      </div>
    </motion.div>
  );
}

function PatternDetailPanel({ pattern, onClose }: { pattern: BehaviorPattern; onClose: () => void }) {
  return (
    <motion.div
      className="glass-card p-6 h-fit sticky top-0"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="section-title">Pattern Details</h3>
        <motion.button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-secondary/50 transition-colors"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <X className="w-4 h-4 text-muted-foreground" />
        </motion.button>
      </div>

      <div className="space-y-6">
        {/* Pattern Header */}
        <div className="flex items-center gap-4">
          <div className={cn(
            'w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-bold font-mono',
            pattern.intentStatus === 'escalated' ? 'bg-destructive/20 text-destructive' :
            pattern.intentStatus === 'elevated' ? 'bg-warning/20 text-warning' :
            'bg-primary/20 text-primary'
          )}>
            {pattern.id}
          </div>
          <div>
            <span className={cn(
              'text-xs font-medium uppercase',
              pattern.intentStatus === 'escalated' ? 'text-destructive' :
              pattern.intentStatus === 'elevated' ? 'text-warning' :
              'text-primary'
            )}>
              {pattern.intentStatus} intent
            </span>
            <p className="text-sm text-foreground mt-1">{pattern.description}</p>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-secondary/30 rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Institutions Observed</p>
            <p className="text-2xl font-bold text-foreground">{pattern.institutionCount}</p>
          </div>
          <div className="bg-secondary/30 rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Time Window</p>
            <p className="text-2xl font-bold text-foreground">{pattern.timeWindow}</p>
          </div>
          <div className="bg-secondary/30 rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Total Occurrences</p>
            <p className="text-2xl font-bold text-foreground">{pattern.occurrences}</p>
          </div>
          <div className="bg-secondary/30 rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Severity Bucket</p>
            <p className={cn(
              'text-2xl font-bold capitalize',
              pattern.severityBucket === 'critical' ? 'text-destructive' :
              pattern.severityBucket === 'high' ? 'text-warning' :
              'text-primary'
            )}>
              {pattern.severityBucket}
            </p>
          </div>
        </div>

        {/* Timeline */}
        <div>
          <p className="subsection-title mb-3">First Seen</p>
          <p className="text-sm text-foreground font-mono">
            {new Date(pattern.firstSeen).toLocaleString()}
          </p>
        </div>
        <div>
          <p className="subsection-title mb-3">Last Seen</p>
          <p className="text-sm text-foreground font-mono">
            {new Date(pattern.lastSeen).toLocaleString()}
          </p>
        </div>

        {/* Escalation History */}
        {pattern.escalationHistory.length > 0 && (
          <div>
            <p className="subsection-title mb-3">Escalation History</p>
            <div className="space-y-2">
              {pattern.escalationHistory.map((event, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <span className="text-muted-foreground font-mono text-xs">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                  <ChevronRight className="w-3 h-3 text-muted-foreground" />
                  <span className={cn(
                    'capitalize',
                    event.toStatus === 'escalated' ? 'text-destructive' :
                    event.toStatus === 'elevated' ? 'text-warning' :
                    'text-primary'
                  )}>
                    {event.fromStatus} → {event.toStatus}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default function Patterns() {
  const [selectedPattern, setSelectedPattern] = useState<BehaviorPattern | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  const filteredPatterns = filterStatus
    ? behaviorPatterns.filter(p => p.intentStatus === filterStatus)
    : behaviorPatterns;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">Behavior Patterns</h1>
            <p className="text-muted-foreground mt-1">Behavioral vocabulary across the collective network</p>
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
              All
            </button>
            <button
              onClick={() => setFilterStatus('normal')}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                filterStatus === 'normal' ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:bg-secondary/50'
              )}
            >
              Normal
            </button>
            <button
              onClick={() => setFilterStatus('elevated')}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                filterStatus === 'elevated' ? 'bg-warning/20 text-warning' : 'text-muted-foreground hover:bg-secondary/50'
              )}
            >
              Elevated
            </button>
            <button
              onClick={() => setFilterStatus('escalated')}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                filterStatus === 'escalated' ? 'bg-destructive/20 text-destructive' : 'text-muted-foreground hover:bg-secondary/50'
              )}
            >
              Escalated
            </button>
          </div>
        </motion.div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Pattern List */}
          <div className={cn('space-y-4', selectedPattern ? 'lg:col-span-2' : 'lg:col-span-3')}>
            <div className={cn(
              'grid gap-4',
              selectedPattern ? 'grid-cols-1 xl:grid-cols-2' : 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
            )}>
              <AnimatePresence>
                {filteredPatterns.map((pattern) => (
                  <PatternCard
                    key={pattern.id}
                    pattern={pattern}
                    onClick={() => setSelectedPattern(pattern)}
                    isSelected={selectedPattern?.id === pattern.id}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* Detail Panel */}
          <AnimatePresence>
            {selectedPattern && (
              <div className="lg:col-span-1">
                <PatternDetailPanel
                  pattern={selectedPattern}
                  onClose={() => setSelectedPattern(null)}
                />
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </MainLayout>
  );
}
