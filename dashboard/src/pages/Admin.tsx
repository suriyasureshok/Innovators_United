import { useState } from 'react';
import { motion } from 'framer-motion';
import { MainLayout } from '@/components/layout/MainLayout';
import { institutions, auditLog } from '@/data/mockData';
import { cn } from '@/lib/utils';
import { Building2, Shield, Clock, Settings, FileText, ChevronRight, AlertTriangle, CheckCircle } from 'lucide-react';

export default function Admin() {
  const [activeTab, setActiveTab] = useState<'institutions' | 'policies' | 'audit'>('institutions');

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Admin & Governance</h1>
          <p className="text-muted-foreground mt-1">Enterprise controls and audit transparency</p>
        </motion.div>

        {/* Tabs */}
        <div className="flex items-center gap-2 border-b border-border pb-4">
          <button
            onClick={() => setActiveTab('institutions')}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'institutions' ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:bg-secondary/50'
            )}
          >
            <Building2 className="w-4 h-4" />
            Institution Registry
          </button>
          <button
            onClick={() => setActiveTab('policies')}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'policies' ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:bg-secondary/50'
            )}
          >
            <Settings className="w-4 h-4" />
            BRIDGE Policies
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'audit' ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:bg-secondary/50'
            )}
          >
            <FileText className="w-4 h-4" />
            Audit Log
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'institutions' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="glass-card overflow-hidden"
          >
            <div className="p-4 border-b border-border">
              <h3 className="section-title">Participating Institutions</h3>
              <p className="text-sm text-muted-foreground mt-1">Anonymous registry of network participants</p>
            </div>
            <div className="divide-y divide-border">
              {institutions.map((inst) => (
                <div key={inst.id} className="flex items-center justify-between p-4 hover:bg-secondary/20 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      'w-10 h-10 rounded-lg flex items-center justify-center',
                      inst.status === 'active' ? 'bg-primary/20' : 'bg-destructive/20'
                    )}>
                      <Building2 className={cn(
                        'w-5 h-5',
                        inst.status === 'active' ? 'text-primary' : 'text-destructive'
                      )} />
                    </div>
                    <div>
                      <p className="font-mono font-medium text-foreground">{inst.id}</p>
                      <p className="text-xs text-muted-foreground">
                        Last participation: {new Date(inst.lastParticipation).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <span className={cn(
                    'text-xs font-medium px-3 py-1 rounded-full',
                    inst.status === 'active' 
                      ? 'bg-success/20 text-success' 
                      : 'bg-destructive/20 text-destructive'
                  )}>
                    {inst.status}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'policies' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {/* Escalation Thresholds */}
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-6">
                <AlertTriangle className="w-5 h-5 text-primary" />
                <h3 className="section-title">Escalation Thresholds</h3>
              </div>
              
              <div className="space-y-4">
                <div className="bg-secondary/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Minimum Institutions for Escalation</span>
                    <span className="text-lg font-bold text-primary">3</span>
                  </div>
                  <input
                    type="range"
                    min="2"
                    max="10"
                    defaultValue="3"
                    className="w-full h-1 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                </div>

                <div className="bg-secondary/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Time Window (minutes)</span>
                    <span className="text-lg font-bold text-primary">15</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="60"
                    defaultValue="15"
                    className="w-full h-1 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                </div>

                <div className="bg-secondary/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Correlation Threshold</span>
                    <span className="text-lg font-bold text-primary">0.75</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    defaultValue="75"
                    className="w-full h-1 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                </div>
              </div>
            </div>

            {/* Pattern Classes */}
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-6">
                <Shield className="w-5 h-5 text-primary" />
                <h3 className="section-title">Pattern Class Controls</h3>
              </div>
              
              <div className="space-y-3">
                {[
                  { name: 'Velocity Patterns', enabled: true },
                  { name: 'Device Fingerprint Patterns', enabled: true },
                  { name: 'Geographic Anomaly Patterns', enabled: true },
                  { name: 'Channel Switching Patterns', enabled: true },
                  { name: 'Session Fragmentation Patterns', enabled: false },
                  { name: 'Dormant Reactivation Patterns', enabled: true },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between bg-secondary/30 rounded-lg p-3">
                    <span className="text-sm text-foreground">{item.name}</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" defaultChecked={item.enabled} className="sr-only peer" />
                      <div className="w-9 h-5 bg-border rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-muted-foreground after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary peer-checked:after:bg-primary-foreground"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'audit' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="glass-card overflow-hidden"
          >
            <div className="p-4 border-b border-border">
              <h3 className="section-title">Immutable Audit Log</h3>
              <p className="text-sm text-muted-foreground mt-1">Chronological record of all system events</p>
            </div>
            <div className="divide-y divide-border max-h-[500px] overflow-auto">
              {auditLog.map((entry) => {
                const getActionIcon = () => {
                  switch (entry.action) {
                    case 'pattern_observed': return <CheckCircle className="w-4 h-4 text-primary" />;
                    case 'intent_escalated': return <AlertTriangle className="w-4 h-4 text-warning" />;
                    case 'advisory_issued': return <Shield className="w-4 h-4 text-destructive" />;
                    case 'alert_reviewed': return <FileText className="w-4 h-4 text-success" />;
                    default: return <Clock className="w-4 h-4 text-muted-foreground" />;
                  }
                };

                const getActionBadge = () => {
                  switch (entry.action) {
                    case 'pattern_observed': return 'badge-normal';
                    case 'intent_escalated': return 'badge-elevated';
                    case 'advisory_issued': return 'badge-escalated';
                    case 'alert_reviewed': return 'bg-success/20 text-success border border-success/30';
                    default: return 'badge-normal';
                  }
                };

                return (
                  <div key={entry.id} className="flex items-start gap-4 p-4 hover:bg-secondary/20 transition-colors">
                    <div className="p-2 rounded-lg bg-secondary/30">
                      {getActionIcon()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-xs text-muted-foreground">
                          {new Date(entry.timestamp).toLocaleString()}
                        </span>
                        <span className={cn('text-xs font-medium px-2 py-0.5 rounded-full capitalize', getActionBadge())}>
                          {entry.action.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-sm text-foreground">{entry.details}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-1" />
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </div>
    </MainLayout>
  );
}
