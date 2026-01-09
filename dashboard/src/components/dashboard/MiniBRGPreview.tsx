import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { behaviorPatterns, patternCorrelations } from '@/data/mockData';
import { cn } from '@/lib/utils';

export function MiniBRGPreview() {
  const navigate = useNavigate();

  // Calculate positions for pattern nodes in a circular layout
  const centerX = 150;
  const centerY = 120;
  const radius = 80;

  const patternNodes = behaviorPatterns.slice(0, 6).map((pattern, index) => {
    const angle = (index * 2 * Math.PI) / 6 - Math.PI / 2;
    return {
      ...pattern,
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
      size: Math.min(30, 15 + pattern.occurrences / 15),
    };
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'escalated': return 'hsl(0, 72%, 51%)';
      case 'elevated': return 'hsl(38, 92%, 50%)';
      default: return 'hsl(199, 89%, 48%)';
    }
  };

  return (
    <motion.div
      className="glass-card p-6 cursor-pointer hover:glass-card-elevated transition-all"
      onClick={() => navigate('/bridge')}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      whileHover={{ scale: 1.01 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="section-title">BRIDGE Pattern Graph</h3>
          <p className="text-sm text-muted-foreground mt-1">Behavioral pattern correlations</p>
        </div>
        <motion.div
          className="flex items-center gap-2 text-primary text-sm font-medium"
          whileHover={{ x: 4 }}
        >
          View Full Graph
          <ArrowRight className="w-4 h-4" />
        </motion.div>
      </div>

      <div className="relative h-[240px] overflow-hidden">
        <svg width="100%" height="100%" viewBox="0 0 300 240">
          {/* Edges (correlations) */}
          {patternCorrelations.slice(0, 5).map((correlation, index) => {
            const sourceNode = patternNodes.find(n => n.id === correlation.sourcePatternId);
            const targetNode = patternNodes.find(n => n.id === correlation.targetPatternId);
            if (!sourceNode || !targetNode) return null;

            return (
              <motion.line
                key={index}
                x1={sourceNode.x}
                y1={sourceNode.y}
                x2={targetNode.x}
                y2={targetNode.y}
                stroke="hsl(199, 60%, 40%)"
                strokeWidth={1 + correlation.correlationStrength * 2}
                strokeOpacity={0.3 + correlation.correlationStrength * 0.4}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
              />
            );
          })}

          {/* Pattern Nodes */}
          {patternNodes.map((node, index) => (
            <motion.g key={node.id}>
              {/* Glow effect for escalated nodes */}
              {node.intentStatus === 'escalated' && (
                <motion.circle
                  cx={node.x}
                  cy={node.y}
                  r={node.size + 6}
                  fill="none"
                  stroke={getStatusColor(node.intentStatus)}
                  strokeWidth={2}
                  opacity={0.4}
                  animate={{
                    r: [node.size + 6, node.size + 12, node.size + 6],
                    opacity: [0.4, 0.2, 0.4],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />
              )}
              <motion.circle
                cx={node.x}
                cy={node.y}
                r={node.size}
                fill={getStatusColor(node.intentStatus)}
                fillOpacity={0.2}
                stroke={getStatusColor(node.intentStatus)}
                strokeWidth={2}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
              />
              <motion.text
                x={node.x}
                y={node.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="hsl(210, 40%, 96%)"
                fontSize={9}
                fontWeight={600}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
              >
                {node.id}
              </motion.text>
            </motion.g>
          ))}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-0 left-0 flex items-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-primary" />
            Normal
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-warning" />
            Elevated
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-destructive" />
            Escalated
          </div>
        </div>
      </div>
    </motion.div>
  );
}
