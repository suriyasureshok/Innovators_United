// SYNAPSE-FI Mock Data
// All data is pattern-centric - NO entity relationships, NO identities

export interface BehaviorPattern {
  id: string;
  description: string;
  institutionCount: number;
  firstSeen: string;
  lastSeen: string;
  intentStatus: 'normal' | 'elevated' | 'escalated';
  occurrences: number;
  severityBucket: 'low' | 'medium' | 'high' | 'critical';
  timeWindow: string;
  escalationHistory: { timestamp: string; fromStatus: string; toStatus: string }[];
}

export interface PatternCorrelation {
  sourcePatternId: string;
  targetPatternId: string;
  correlationStrength: number; // 0-1
  timeWindowMinutes: number;
}

export interface Alert {
  id: string;
  patternId: string;
  intentLevel: 'elevated' | 'escalated';
  timeWindow: string;
  institutionCount: number;
  timestamp: string;
  confidenceScore: number;
  triggerRule: string;
  status: 'active' | 'reviewed' | 'dismissed';
}

export interface Institution {
  id: string;
  status: 'active' | 'suspended';
  lastParticipation: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  action: 'pattern_observed' | 'intent_escalated' | 'advisory_issued' | 'alert_reviewed';
  details: string;
}

export interface TimelineDataPoint {
  timestamp: string;
  normalPatterns: number;
  elevatedPatterns: number;
  escalatedPatterns: number;
}

// Mock Behavior Patterns
export const behaviorPatterns: BehaviorPattern[] = [
  {
    id: 'X92F',
    description: 'High velocity + new device fingerprint',
    institutionCount: 3,
    firstSeen: '2024-01-15T08:23:00Z',
    lastSeen: '2024-01-15T14:45:00Z',
    intentStatus: 'escalated',
    occurrences: 47,
    severityBucket: 'critical',
    timeWindow: '4 minutes',
    escalationHistory: [
      { timestamp: '2024-01-15T10:00:00Z', fromStatus: 'normal', toStatus: 'elevated' },
      { timestamp: '2024-01-15T14:30:00Z', fromStatus: 'elevated', toStatus: 'escalated' },
    ],
  },
  {
    id: 'K7M2',
    description: 'Dormant account reactivation + immediate high-value behavior',
    institutionCount: 5,
    firstSeen: '2024-01-14T12:00:00Z',
    lastSeen: '2024-01-15T14:20:00Z',
    intentStatus: 'elevated',
    occurrences: 23,
    severityBucket: 'high',
    timeWindow: '15 minutes',
    escalationHistory: [
      { timestamp: '2024-01-15T09:00:00Z', fromStatus: 'normal', toStatus: 'elevated' },
    ],
  },
  {
    id: 'P3R9',
    description: 'Rapid channel switching behavior',
    institutionCount: 2,
    firstSeen: '2024-01-15T06:00:00Z',
    lastSeen: '2024-01-15T14:10:00Z',
    intentStatus: 'normal',
    occurrences: 156,
    severityBucket: 'low',
    timeWindow: '30 minutes',
    escalationHistory: [],
  },
  {
    id: 'T8N4',
    description: 'Geographic anomaly + timing pattern deviation',
    institutionCount: 4,
    firstSeen: '2024-01-13T18:00:00Z',
    lastSeen: '2024-01-15T13:55:00Z',
    intentStatus: 'escalated',
    occurrences: 31,
    severityBucket: 'critical',
    timeWindow: '8 minutes',
    escalationHistory: [
      { timestamp: '2024-01-14T12:00:00Z', fromStatus: 'normal', toStatus: 'elevated' },
      { timestamp: '2024-01-15T13:00:00Z', fromStatus: 'elevated', toStatus: 'escalated' },
    ],
  },
  {
    id: 'V2L6',
    description: 'Session fragmentation pattern',
    institutionCount: 7,
    firstSeen: '2024-01-10T09:00:00Z',
    lastSeen: '2024-01-15T14:00:00Z',
    intentStatus: 'elevated',
    occurrences: 89,
    severityBucket: 'medium',
    timeWindow: '20 minutes',
    escalationHistory: [
      { timestamp: '2024-01-15T11:00:00Z', fromStatus: 'normal', toStatus: 'elevated' },
    ],
  },
  {
    id: 'A5Q1',
    description: 'Behavioral velocity spike',
    institutionCount: 3,
    firstSeen: '2024-01-15T10:00:00Z',
    lastSeen: '2024-01-15T14:35:00Z',
    intentStatus: 'normal',
    occurrences: 212,
    severityBucket: 'low',
    timeWindow: '45 minutes',
    escalationHistory: [],
  },
  {
    id: 'D9W3',
    description: 'Cross-channel pattern synchronization',
    institutionCount: 6,
    firstSeen: '2024-01-12T14:00:00Z',
    lastSeen: '2024-01-15T14:25:00Z',
    intentStatus: 'escalated',
    occurrences: 18,
    severityBucket: 'critical',
    timeWindow: '3 minutes',
    escalationHistory: [
      { timestamp: '2024-01-14T08:00:00Z', fromStatus: 'normal', toStatus: 'elevated' },
      { timestamp: '2024-01-15T14:00:00Z', fromStatus: 'elevated', toStatus: 'escalated' },
    ],
  },
  {
    id: 'H4E8',
    description: 'Recurring micro-pattern cluster',
    institutionCount: 2,
    firstSeen: '2024-01-15T07:30:00Z',
    lastSeen: '2024-01-15T13:45:00Z',
    intentStatus: 'normal',
    occurrences: 67,
    severityBucket: 'low',
    timeWindow: '60 minutes',
    escalationHistory: [],
  },
];

// Pattern Correlations (for BRIDGE visualization)
export const patternCorrelations: PatternCorrelation[] = [
  { sourcePatternId: 'X92F', targetPatternId: 'T8N4', correlationStrength: 0.87, timeWindowMinutes: 4 },
  { sourcePatternId: 'X92F', targetPatternId: 'D9W3', correlationStrength: 0.72, timeWindowMinutes: 6 },
  { sourcePatternId: 'K7M2', targetPatternId: 'V2L6', correlationStrength: 0.65, timeWindowMinutes: 15 },
  { sourcePatternId: 'T8N4', targetPatternId: 'D9W3', correlationStrength: 0.91, timeWindowMinutes: 3 },
  { sourcePatternId: 'V2L6', targetPatternId: 'A5Q1', correlationStrength: 0.45, timeWindowMinutes: 30 },
  { sourcePatternId: 'P3R9', targetPatternId: 'H4E8', correlationStrength: 0.38, timeWindowMinutes: 25 },
  { sourcePatternId: 'K7M2', targetPatternId: 'T8N4', correlationStrength: 0.58, timeWindowMinutes: 12 },
];

// Alerts
export const alerts: Alert[] = [
  {
    id: 'ALT-001',
    patternId: 'X92F',
    intentLevel: 'escalated',
    timeWindow: '14:30 - 14:45',
    institutionCount: 3,
    timestamp: '2024-01-15T14:45:00Z',
    confidenceScore: 0.94,
    triggerRule: 'Cross-institution threshold (3+) within 4-minute window',
    status: 'active',
  },
  {
    id: 'ALT-002',
    patternId: 'T8N4',
    intentLevel: 'escalated',
    timeWindow: '13:45 - 14:00',
    institutionCount: 4,
    timestamp: '2024-01-15T14:00:00Z',
    confidenceScore: 0.89,
    triggerRule: 'Geographic anomaly correlation exceeded 0.85',
    status: 'active',
  },
  {
    id: 'ALT-003',
    patternId: 'D9W3',
    intentLevel: 'escalated',
    timeWindow: '14:20 - 14:25',
    institutionCount: 6,
    timestamp: '2024-01-15T14:25:00Z',
    confidenceScore: 0.92,
    triggerRule: 'Synchronized pattern detected across 6 institutions',
    status: 'active',
  },
  {
    id: 'ALT-004',
    patternId: 'K7M2',
    intentLevel: 'elevated',
    timeWindow: '08:45 - 09:15',
    institutionCount: 5,
    timestamp: '2024-01-15T09:15:00Z',
    confidenceScore: 0.78,
    triggerRule: 'Dormant reactivation pattern velocity threshold',
    status: 'reviewed',
  },
  {
    id: 'ALT-005',
    patternId: 'V2L6',
    intentLevel: 'elevated',
    timeWindow: '10:50 - 11:10',
    institutionCount: 7,
    timestamp: '2024-01-15T11:10:00Z',
    confidenceScore: 0.71,
    triggerRule: 'Session fragmentation spread rate exceeded normal',
    status: 'reviewed',
  },
];

// Institutions (anonymous)
export const institutions: Institution[] = [
  { id: 'INST-A1', status: 'active', lastParticipation: '2024-01-15T14:45:00Z' },
  { id: 'INST-B2', status: 'active', lastParticipation: '2024-01-15T14:40:00Z' },
  { id: 'INST-C3', status: 'active', lastParticipation: '2024-01-15T14:38:00Z' },
  { id: 'INST-D4', status: 'active', lastParticipation: '2024-01-15T14:35:00Z' },
  { id: 'INST-E5', status: 'active', lastParticipation: '2024-01-15T14:30:00Z' },
  { id: 'INST-F6', status: 'active', lastParticipation: '2024-01-15T14:25:00Z' },
  { id: 'INST-G7', status: 'suspended', lastParticipation: '2024-01-14T18:00:00Z' },
  { id: 'INST-H8', status: 'active', lastParticipation: '2024-01-15T14:20:00Z' },
];

// Audit Log
export const auditLog: AuditLogEntry[] = [
  { id: 'LOG-001', timestamp: '2024-01-15T14:45:00Z', action: 'advisory_issued', details: 'Global intent advisory for pattern X92F' },
  { id: 'LOG-002', timestamp: '2024-01-15T14:30:00Z', action: 'intent_escalated', details: 'Pattern X92F escalated from elevated to escalated' },
  { id: 'LOG-003', timestamp: '2024-01-15T14:25:00Z', action: 'advisory_issued', details: 'Global intent advisory for pattern D9W3' },
  { id: 'LOG-004', timestamp: '2024-01-15T14:00:00Z', action: 'intent_escalated', details: 'Pattern D9W3 escalated from elevated to escalated' },
  { id: 'LOG-005', timestamp: '2024-01-15T13:55:00Z', action: 'pattern_observed', details: 'Pattern T8N4 observed in 4th institution' },
  { id: 'LOG-006', timestamp: '2024-01-15T13:00:00Z', action: 'intent_escalated', details: 'Pattern T8N4 escalated from elevated to escalated' },
  { id: 'LOG-007', timestamp: '2024-01-15T11:10:00Z', action: 'alert_reviewed', details: 'Alert ALT-005 reviewed and acknowledged' },
  { id: 'LOG-008', timestamp: '2024-01-15T11:00:00Z', action: 'intent_escalated', details: 'Pattern V2L6 escalated from normal to elevated' },
  { id: 'LOG-009', timestamp: '2024-01-15T09:15:00Z', action: 'alert_reviewed', details: 'Alert ALT-004 reviewed and acknowledged' },
  { id: 'LOG-010', timestamp: '2024-01-15T09:00:00Z', action: 'intent_escalated', details: 'Pattern K7M2 escalated from normal to elevated' },
];

// Timeline Data (for Overview chart)
export const timelineData: TimelineDataPoint[] = [
  { timestamp: '08:00', normalPatterns: 45, elevatedPatterns: 2, escalatedPatterns: 0 },
  { timestamp: '09:00', normalPatterns: 52, elevatedPatterns: 5, escalatedPatterns: 0 },
  { timestamp: '10:00', normalPatterns: 61, elevatedPatterns: 8, escalatedPatterns: 1 },
  { timestamp: '11:00', normalPatterns: 58, elevatedPatterns: 12, escalatedPatterns: 1 },
  { timestamp: '12:00', normalPatterns: 49, elevatedPatterns: 15, escalatedPatterns: 2 },
  { timestamp: '13:00', normalPatterns: 67, elevatedPatterns: 18, escalatedPatterns: 2 },
  { timestamp: '14:00', normalPatterns: 72, elevatedPatterns: 14, escalatedPatterns: 3 },
  { timestamp: '14:30', normalPatterns: 68, elevatedPatterns: 11, escalatedPatterns: 3 },
  { timestamp: '14:45', normalPatterns: 65, elevatedPatterns: 9, escalatedPatterns: 3 },
];

// KPI Data
export const kpiData = {
  activeInstitutions: 7,
  institutionTrend: '+2',
  activeBehaviorPatterns: 8,
  patternTrend: '+12',
  escalatedIntents: 3,
  escalatedTrend: '+1',
  alertsLast10Min: 2,
  alertsTrend: '-3',
};
