import { MainLayout } from '@/components/layout/MainLayout';
import { KPICard } from '@/components/dashboard/KPICard';
import { PatternTimeline } from '@/components/dashboard/PatternTimeline';
import { MiniBRGPreview } from '@/components/dashboard/MiniBRGPreview';
import { kpiData } from '@/data/mockData';
import { Building2, Fingerprint, AlertOctagon, Bell } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Overview() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h1 className="text-2xl font-bold text-foreground tracking-tight">System Overview</h1>
          <p className="text-muted-foreground mt-1">Real-time collective fraud intelligence awareness</p>
        </motion.div>

        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Active Institutions"
            value={kpiData.activeInstitutions}
            trend={kpiData.institutionTrend}
            icon={Building2}
          />
          <KPICard
            title="Active Behavior Patterns"
            value={kpiData.activeBehaviorPatterns}
            trend={kpiData.patternTrend}
            icon={Fingerprint}
          />
          <KPICard
            title="Escalated Intents (BRIDGE)"
            value={kpiData.escalatedIntents}
            trend={kpiData.escalatedTrend}
            icon={AlertOctagon}
            variant="danger"
          />
          <KPICard
            title="Alerts (Last 10 min)"
            value={kpiData.alertsLast10Min}
            trend={kpiData.alertsTrend}
            icon={Bell}
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <PatternTimeline />
          </div>
          <div className="lg:col-span-1">
            <MiniBRGPreview />
          </div>
        </div>

        {/* Quick Status Banner */}
        <motion.div
          className="glass-card-danger p-4 flex items-center justify-between"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-destructive/20 flex items-center justify-center">
              <AlertOctagon className="w-5 h-5 text-destructive" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Coordinated behavior detected</p>
              <p className="text-xs text-muted-foreground">Pattern X92F observed across 3 institutions within 4 minutes</p>
            </div>
          </div>
          <motion.button
            className="px-4 py-2 bg-destructive/20 hover:bg-destructive/30 text-destructive text-sm font-medium rounded-lg transition-colors"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            View Details
          </motion.button>
        </motion.div>
      </div>
    </MainLayout>
  );
}
