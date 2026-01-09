import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Fingerprint,
  Network,
  AlertTriangle,
  Shield,
  GitBranch,
  Zap,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/patterns', label: 'Patterns', icon: Fingerprint },
  { path: '/bridge', label: 'BRIDGE Intelligence', icon: Network },
  { path: '/alerts', label: 'Alerts & Explainability', icon: AlertTriangle },
  { path: '/admin', label: 'Admin & Governance', icon: Shield },
  { path: '/architecture', label: 'Architecture & Data Flow', icon: GitBranch },
];

export function AppSidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 min-h-screen bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
            <Zap className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground tracking-tight">SYNAPSE-FI</h1>
            <p className="text-[10px] text-muted-foreground leading-tight">Privacy-Preserving Collective<br />Fraud Intelligence</p>
          </div>
        </div>
        <div className="mt-3">
          <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-primary/10 border border-primary/20 text-[10px] font-medium text-primary">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            Powered by BRIDGE
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className="block"
            >
              <motion.div
                className={isActive ? 'nav-item-active' : 'nav-item'}
                whileHover={{ x: 4 }}
                transition={{ duration: 0.15 }}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm font-medium">{item.label}</span>
              </motion.div>
            </NavLink>
          );
        })}
      </nav>

      {/* Status Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="glass-card p-3">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span className="text-xs font-medium text-foreground">System Operational</span>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Last sync: 2 seconds ago
          </p>
        </div>
      </div>
    </aside>
  );
}
