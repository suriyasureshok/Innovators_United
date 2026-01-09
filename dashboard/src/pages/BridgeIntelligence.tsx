import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MainLayout } from '@/components/layout/MainLayout';
import { behaviorPatterns, patternCorrelations, BehaviorPattern } from '@/data/mockData';
import { cn } from '@/lib/utils';
import { Info, Zap, Building2, Clock, ChevronRight, X } from 'lucide-react';

function BridgeExplanation({ pattern }: { pattern: BehaviorPattern | null }) {
  const steps = [
    { label: 'Local Observation', description: 'Institution detects behavioral pattern locally' },
    { label: 'Fingerprint Generation', description: 'Pattern converted to privacy-preserving fingerprint' },
    { label: 'Cross-Institution Correlation', description: 'BRIDGE correlates fingerprints without raw data' },
    { label: 'Intent Threshold Analysis', description: 'Escalation rules evaluated across network' },
    { label: 'Advisory Generation', description: 'Global intent advisory issued to participants' },
  ];

  return (
    <div className="glass-card p-6 h-full">
      <div className="flex items-center gap-2 mb-6">
        <Zap className="w-5 h-5 text-primary" />
        <h3 className="section-title">BRIDGE Explanation</h3>
      </div>

      {pattern ? (
        <div className="space-y-4">
          <div className="bg-secondary/30 rounded-lg p-4 mb-6">
            <p className="text-xs text-muted-foreground mb-1">Selected Pattern</p>
            <div className="flex items-center gap-3">
              <span className="text-xl font-bold text-primary font-mono">{pattern.id}</span>
              <span className={cn(
                'text-xs font-medium uppercase',
                pattern.intentStatus === 'escalated' ? 'text-destructive' :
                pattern.intentStatus === 'elevated' ? 'text-warning' :
                'text-primary'
              )}>
                {pattern.intentStatus}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mt-2">{pattern.description}</p>
          </div>

          <p className="subsection-title">Detection Flow</p>
          <div className="space-y-1">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                className={cn(
                  'explanation-step',
                  index <= (pattern.intentStatus === 'escalated' ? 4 : pattern.intentStatus === 'elevated' ? 3 : 2) && 'explanation-step-active'
                )}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <p className="text-sm font-medium text-foreground">{step.label}</p>
                <p className="text-xs text-muted-foreground">{step.description}</p>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-border">
            <p className="subsection-title mb-3">Pattern Metrics</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center gap-2 text-sm">
                <Building2 className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Institutions:</span>
                <span className="font-medium text-foreground">{pattern.institutionCount}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Window:</span>
                <span className="font-medium text-foreground">{pattern.timeWindow}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <Info className="w-10 h-10 text-muted-foreground mb-4" />
          <p className="text-sm text-muted-foreground">Select a pattern node to view<br />BRIDGE explanation details</p>
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground leading-relaxed">
          <strong className="text-foreground">Privacy Note:</strong> Raw transaction data never leaves institutions. 
          BRIDGE correlates behavioral fingerprints only — no identities are stored or shared globally.
        </p>
      </div>
    </div>
  );
}

export default function BridgeIntelligence() {
  const [selectedPattern, setSelectedPattern] = useState<BehaviorPattern | null>(null);
  const [hoveredPattern, setHoveredPattern] = useState<string | null>(null);

  // Calculate node positions with force-directed-like layout
  const nodePositions = useMemo(() => {
    const width = 800;
    const height = 500;
    const centerX = width / 2;
    const centerY = height / 2;

    // Arrange escalated patterns in center, others in outer ring
    const escalated = behaviorPatterns.filter(p => p.intentStatus === 'escalated');
    const elevated = behaviorPatterns.filter(p => p.intentStatus === 'elevated');
    const normal = behaviorPatterns.filter(p => p.intentStatus === 'normal');

    const positions: Record<string, { x: number; y: number; size: number }> = {};

    // Center escalated patterns
    escalated.forEach((p, i) => {
      const angle = (i * 2 * Math.PI) / Math.max(escalated.length, 1);
      positions[p.id] = {
        x: centerX + 80 * Math.cos(angle),
        y: centerY + 80 * Math.sin(angle),
        size: 45 + p.occurrences / 10,
      };
    });

    // Middle ring for elevated
    elevated.forEach((p, i) => {
      const angle = (i * 2 * Math.PI) / Math.max(elevated.length, 1) + Math.PI / 4;
      positions[p.id] = {
        x: centerX + 180 * Math.cos(angle),
        y: centerY + 180 * Math.sin(angle),
        size: 35 + p.occurrences / 15,
      };
    });

    // Outer ring for normal
    normal.forEach((p, i) => {
      const angle = (i * 2 * Math.PI) / Math.max(normal.length, 1) + Math.PI / 6;
      positions[p.id] = {
        x: centerX + 280 * Math.cos(angle),
        y: centerY + 280 * Math.sin(angle),
        size: 30 + p.occurrences / 20,
      };
    });

    return positions;
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'escalated': return 'hsl(0, 72%, 51%)';
      case 'elevated': return 'hsl(38, 92%, 50%)';
      default: return 'hsl(199, 89%, 48%)';
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6 h-full">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h1 className="text-2xl font-bold text-foreground tracking-tight">BRIDGE Intelligence</h1>
          <p className="text-muted-foreground mt-1">Behavioral Risk Intent Discovery Engine — Pattern correlation visualization</p>
        </motion.div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-220px)]">
          {/* Graph Visualization */}
          <motion.div
            className="lg:col-span-3 glass-card p-4 overflow-hidden"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <svg width="100%" height="100%" viewBox="0 0 800 500" className="min-h-[400px]">
              {/* Grid Background */}
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="hsl(222, 30%, 15%)" strokeWidth="0.5" />
                </pattern>
                <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="hsl(199, 89%, 48%)" stopOpacity="0.1" />
                  <stop offset="100%" stopColor="hsl(199, 89%, 48%)" stopOpacity="0" />
                </radialGradient>
              </defs>
              <rect width="800" height="500" fill="url(#grid)" />
              <circle cx="400" cy="250" r="150" fill="url(#centerGlow)" />

              {/* Edges (correlations) */}
              {patternCorrelations.map((correlation, index) => {
                const source = nodePositions[correlation.sourcePatternId];
                const target = nodePositions[correlation.targetPatternId];
                if (!source || !target) return null;

                const isHighlighted = hoveredPattern === correlation.sourcePatternId || 
                                      hoveredPattern === correlation.targetPatternId ||
                                      selectedPattern?.id === correlation.sourcePatternId ||
                                      selectedPattern?.id === correlation.targetPatternId;

                return (
                  <motion.line
                    key={index}
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    stroke="hsl(199, 60%, 40%)"
                    strokeWidth={isHighlighted ? 3 : 1 + correlation.correlationStrength * 2}
                    strokeOpacity={isHighlighted ? 0.8 : 0.2 + correlation.correlationStrength * 0.3}
                    initial={{ pathLength: 0 }}
                    animate={{ 
                      pathLength: 1,
                      strokeOpacity: isHighlighted ? 0.8 : 0.2 + correlation.correlationStrength * 0.3 
                    }}
                    transition={{ duration: 0.8, delay: index * 0.05 }}
                  />
                );
              })}

              {/* Pattern Nodes */}
              {behaviorPatterns.map((pattern, index) => {
                const pos = nodePositions[pattern.id];
                if (!pos) return null;

                const isSelected = selectedPattern?.id === pattern.id;
                const isHovered = hoveredPattern === pattern.id;

                return (
                  <motion.g
                    key={pattern.id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPattern(pattern)}
                    onMouseEnter={() => setHoveredPattern(pattern.id)}
                    onMouseLeave={() => setHoveredPattern(null)}
                  >
                    {/* Glow effect */}
                    {(pattern.intentStatus === 'escalated' || isSelected) && (
                      <motion.circle
                        cx={pos.x}
                        cy={pos.y}
                        r={pos.size + 10}
                        fill="none"
                        stroke={getStatusColor(pattern.intentStatus)}
                        strokeWidth={2}
                        opacity={0.5}
                        animate={{
                          r: [pos.size + 10, pos.size + 20, pos.size + 10],
                          opacity: [0.5, 0.2, 0.5],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: 'easeInOut',
                        }}
                      />
                    )}

                    {/* Selection ring */}
                    {isSelected && (
                      <circle
                        cx={pos.x}
                        cy={pos.y}
                        r={pos.size + 5}
                        fill="none"
                        stroke="hsl(210, 40%, 96%)"
                        strokeWidth={2}
                        strokeDasharray="4 4"
                      />
                    )}

                    {/* Node */}
                    <motion.circle
                      cx={pos.x}
                      cy={pos.y}
                      r={pos.size}
                      fill={getStatusColor(pattern.intentStatus)}
                      fillOpacity={isHovered || isSelected ? 0.4 : 0.2}
                      stroke={getStatusColor(pattern.intentStatus)}
                      strokeWidth={isHovered || isSelected ? 3 : 2}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.4, delay: 0.2 + index * 0.05 }}
                      whileHover={{ scale: 1.1 }}
                    />

                    {/* Label */}
                    <motion.text
                      x={pos.x}
                      y={pos.y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="hsl(210, 40%, 96%)"
                      fontSize={14}
                      fontWeight={700}
                      fontFamily="monospace"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3, delay: 0.4 + index * 0.05 }}
                    >
                      {pattern.id}
                    </motion.text>

                    {/* Occurrence count */}
                    <motion.text
                      x={pos.x}
                      y={pos.y + 18}
                      textAnchor="middle"
                      fill="hsl(215, 20%, 55%)"
                      fontSize={10}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3, delay: 0.5 + index * 0.05 }}
                    >
                      {pattern.occurrences}×
                    </motion.text>
                  </motion.g>
                );
              })}

              {/* Legend */}
              <g transform="translate(20, 450)">
                <text x="0" y="0" fill="hsl(215, 20%, 55%)" fontSize="10" fontWeight="500">NODE LEGEND</text>
                <circle cx="10" cy="20" r="6" fill="hsl(199, 89%, 48%)" fillOpacity="0.3" stroke="hsl(199, 89%, 48%)" strokeWidth="1.5" />
                <text x="24" y="24" fill="hsl(210, 40%, 96%)" fontSize="11">Normal</text>
                <circle cx="90" cy="20" r="6" fill="hsl(38, 92%, 50%)" fillOpacity="0.3" stroke="hsl(38, 92%, 50%)" strokeWidth="1.5" />
                <text x="104" y="24" fill="hsl(210, 40%, 96%)" fontSize="11">Elevated</text>
                <circle cx="180" cy="20" r="6" fill="hsl(0, 72%, 51%)" fillOpacity="0.3" stroke="hsl(0, 72%, 51%)" strokeWidth="1.5" />
                <text x="194" y="24" fill="hsl(210, 40%, 96%)" fontSize="11">Escalated</text>
              </g>
            </svg>
          </motion.div>

          {/* Explanation Panel */}
          <div className="lg:col-span-1">
            <BridgeExplanation pattern={selectedPattern} />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
