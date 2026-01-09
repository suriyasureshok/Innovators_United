import { motion } from 'framer-motion';
import { MainLayout } from '@/components/layout/MainLayout';
import { Database, Lock, Eye, Fingerprint, Network, Shield, ArrowRight, CheckCircle } from 'lucide-react';

export default function Architecture() {
  const dataFlowSteps = [
    {
      icon: Database,
      title: 'Transaction',
      subtitle: 'Local Only',
      description: 'Raw transaction data processed locally at institution',
      color: 'primary',
      badge: 'Never Leaves',
    },
    {
      icon: Eye,
      title: 'Behavioral Signals',
      subtitle: 'Local Extraction',
      description: 'Behavioral attributes extracted without identity linkage',
      color: 'primary',
      badge: 'Privacy-Safe',
    },
    {
      icon: Fingerprint,
      title: 'Behavior Pattern',
      subtitle: 'Anonymous',
      description: 'Pattern classified using standardized behavioral vocabulary',
      color: 'primary',
      badge: 'No PII',
    },
    {
      icon: Lock,
      title: 'Risk Fingerprint',
      subtitle: 'Encrypted',
      description: 'Cryptographic fingerprint generated for sharing',
      color: 'warning',
      badge: 'One-Way Hash',
    },
    {
      icon: Network,
      title: 'BRIDGE Correlation',
      subtitle: 'Collective',
      description: 'Fingerprints correlated across institutions',
      color: 'warning',
      badge: 'No Raw Data',
    },
    {
      icon: Shield,
      title: 'Intent Advisory',
      subtitle: 'Actionable',
      description: 'Global intent state shared with participants',
      color: 'destructive',
      badge: 'Collective Intel',
    },
  ];

  const privacyGuarantees = [
    'Raw transaction data never leaves institutions',
    'No individual identities stored or shared globally',
    'All correlation happens on behavioral fingerprints only',
    'Decisions and actions remain local to each institution',
    'Deterministic algorithms — no black-box AI',
    'Complete audit trail for regulatory compliance',
  ];

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Architecture & Data Flow</h1>
          <p className="text-muted-foreground mt-1">Privacy-preserving intelligence architecture explained</p>
        </motion.div>

        {/* Data Flow Diagram */}
        <motion.div
          className="glass-card p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h3 className="section-title mb-6">Data Transformation Pipeline</h3>
          <p className="text-sm text-muted-foreground mb-8">
            Each step transforms data while preserving privacy. Raw information never crosses institutional boundaries.
          </p>

          <div className="relative">
            {/* Flow Steps */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
              {dataFlowSteps.map((step, index) => {
                const Icon = step.icon;
                const colorClasses = {
                  primary: 'bg-primary/20 text-primary border-primary/30',
                  warning: 'bg-warning/20 text-warning border-warning/30',
                  destructive: 'bg-destructive/20 text-destructive border-destructive/30',
                };

                return (
                  <motion.div
                    key={index}
                    className="relative"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <div className={`glass-card p-4 h-full border ${step.color === 'destructive' ? 'border-destructive/30' : step.color === 'warning' ? 'border-warning/30' : 'border-border'}`}>
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${colorClasses[step.color as keyof typeof colorClasses]}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <div className="mb-2">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colorClasses[step.color as keyof typeof colorClasses]}`}>
                          {step.badge}
                        </span>
                      </div>
                      <h4 className="font-semibold text-foreground">{step.title}</h4>
                      <p className="text-xs text-muted-foreground mb-2">{step.subtitle}</p>
                      <p className="text-xs text-muted-foreground">{step.description}</p>
                    </div>

                    {/* Arrow */}
                    {index < dataFlowSteps.length - 1 && (
                      <div className="hidden xl:flex absolute top-1/2 -right-2 transform -translate-y-1/2 z-10">
                        <ArrowRight className="w-4 h-4 text-muted-foreground" />
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Privacy Guarantees */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div
            className="glass-card p-6"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <div className="flex items-center gap-2 mb-6">
              <Shield className="w-5 h-5 text-success" />
              <h3 className="section-title">Privacy Guarantees</h3>
            </div>

            <div className="space-y-3">
              {privacyGuarantees.map((guarantee, index) => (
                <motion.div
                  key={index}
                  className="flex items-start gap-3"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: 0.3 + index * 0.05 }}
                >
                  <CheckCircle className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-foreground">{guarantee}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          <motion.div
            className="glass-card p-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            <div className="flex items-center gap-2 mb-6">
              <Network className="w-5 h-5 text-primary" />
              <h3 className="section-title">BRIDGE Algorithm</h3>
            </div>

            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">B</strong>ehavioral <strong className="text-foreground">R</strong>isk <strong className="text-foreground">I</strong>ntent <strong className="text-foreground">D</strong>iscovery <strong className="text-foreground">G</strong>raph <strong className="text-foreground">E</strong>ngine
              </p>

              <div className="bg-secondary/30 rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-3">Core Principles</p>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2 text-sm text-foreground">
                    <span className="text-primary">•</span>
                    Pattern-centric analysis (not entity-centric)
                  </li>
                  <li className="flex items-start gap-2 text-sm text-foreground">
                    <span className="text-primary">•</span>
                    Temporal correlation without identity linkage
                  </li>
                  <li className="flex items-start gap-2 text-sm text-foreground">
                    <span className="text-primary">•</span>
                    Deterministic escalation rules
                  </li>
                  <li className="flex items-start gap-2 text-sm text-foreground">
                    <span className="text-primary">•</span>
                    Explainable intent classification
                  </li>
                </ul>
              </div>

              <div className="bg-primary/10 rounded-lg p-4 border border-primary/30">
                <p className="text-xs text-primary font-medium mb-1">Key Innovation</p>
                <p className="text-sm text-foreground">
                  BRIDGE enables collective fraud intelligence without creating a centralized 
                  surveillance system. Privacy is mathematically guaranteed, not promised.
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Architecture Diagram */}
        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.4 }}
        >
          <h3 className="section-title mb-6">System Architecture</h3>
          
          <div className="relative h-[300px] overflow-hidden">
            <svg viewBox="0 0 800 280" className="w-full h-full">
              {/* Institution boxes */}
              {[0, 1, 2].map((i) => (
                <g key={i} transform={`translate(${50 + i * 180}, 30)`}>
                  <rect width="140" height="80" rx="8" fill="hsl(222, 30%, 12%)" stroke="hsl(199, 89%, 48%)" strokeWidth="1" strokeOpacity="0.5" />
                  <text x="70" y="35" textAnchor="middle" fill="hsl(210, 40%, 96%)" fontSize="11" fontWeight="500">Institution {i + 1}</text>
                  <text x="70" y="55" textAnchor="middle" fill="hsl(215, 20%, 55%)" fontSize="9">Local Processing</text>
                  <text x="70" y="68" textAnchor="middle" fill="hsl(199, 89%, 48%)" fontSize="8">DATA STAYS HERE</text>
                </g>
              ))}

              {/* Arrows to BRIDGE */}
              {[0, 1, 2].map((i) => (
                <g key={`arrow-${i}`}>
                  <line 
                    x1={120 + i * 180} y1="110" 
                    x2={400} y2="160" 
                    stroke="hsl(199, 60%, 40%)" 
                    strokeWidth="1.5" 
                    strokeDasharray="4 4"
                    strokeOpacity="0.6"
                  />
                  <text 
                    x={(120 + i * 180 + 400) / 2 - 20} 
                    y={(110 + 160) / 2 - 5} 
                    fill="hsl(215, 20%, 55%)" 
                    fontSize="8"
                    transform={`rotate(-15, ${(120 + i * 180 + 400) / 2}, ${(110 + 160) / 2})`}
                  >
                    Fingerprints Only
                  </text>
                </g>
              ))}

              {/* BRIDGE Core */}
              <g transform="translate(320, 150)">
                <rect width="160" height="70" rx="8" fill="hsl(222, 47%, 8%)" stroke="hsl(38, 92%, 50%)" strokeWidth="2" />
                <text x="80" y="30" textAnchor="middle" fill="hsl(38, 92%, 50%)" fontSize="12" fontWeight="700">BRIDGE</text>
                <text x="80" y="48" textAnchor="middle" fill="hsl(210, 40%, 96%)" fontSize="9">Correlation Engine</text>
                <text x="80" y="60" textAnchor="middle" fill="hsl(215, 20%, 55%)" fontSize="8">No Raw Data Access</text>
              </g>

              {/* Output */}
              <g transform="translate(560, 155)">
                <rect width="180" height="60" rx="8" fill="hsl(222, 30%, 12%)" stroke="hsl(0, 72%, 51%)" strokeWidth="1.5" />
                <text x="90" y="28" textAnchor="middle" fill="hsl(0, 72%, 51%)" fontSize="11" fontWeight="500">Intent Advisories</text>
                <text x="90" y="45" textAnchor="middle" fill="hsl(210, 40%, 96%)" fontSize="9">Collective Intelligence Output</text>
              </g>

              {/* Arrow to output */}
              <line x1="480" y1="185" x2="555" y2="185" stroke="hsl(0, 72%, 51%)" strokeWidth="2" markerEnd="url(#arrowhead)" />
              
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="hsl(0, 72%, 51%)" />
                </marker>
              </defs>
            </svg>
          </div>
        </motion.div>
      </div>
    </MainLayout>
  );
}
