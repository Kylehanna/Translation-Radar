export const ROUTE_PATHS = {
  HOME: '/',
  SEARCH: '/',
  COVERAGE: '/coverage',
  CATALOGS: '/catalogs',
  AGENT_RUNS: '/agent-runs',
  CLUSTERS: '/clusters',
} as const;

export enum AgentStatus {
  CRAWLING = 'CRAWLING',
  VALIDATING = 'VALIDATING',
  SUMMARIZING = 'SUMMARIZING',
  IDLE = 'IDLE',
  ERROR = 'ERROR',
  QUEUED = 'QUEUED',
  COMPLETED = 'COMPLETED',
  RUNNING = 'RUNNING',
  FAILED = 'FAILED',
}

export enum LicensingStatus {
  AVAILABLE = 'AVAILABLE',
  LICENSED = 'LICENSED',
  PENDING = 'PENDING',
  NOT_AVAILABLE = 'NOT_AVAILABLE',
  CONTACT_TTO = 'CONTACT_TTO',
}

export enum TechDomain {
  ONCOLOGY = 'ONCOLOGY',
  AI_ML = 'AI_ML',
  MEDICAL_IMAGING = 'MEDICAL_IMAGING',
  BIOTECH = 'BIOTECH',
  CLEANTECH = 'CLEANTECH',
  MEDTECH = 'MEDTECH',
  MATERIALS = 'MATERIALS',
  DIAGNOSTICS = 'DIAGNOSTICS',
  THERAPEUTICS = 'THERAPEUTICS',
  DEVICES = 'DEVICES',
}

export enum ProvenanceLevel {
  DIRECT_SOURCE_VERIFIED = 'DIRECT_SOURCE_VERIFIED',
  AGENT_VALIDATED = 'AGENT_VALIDATED',
  NEEDS_REVIEW = 'NEEDS_REVIEW',
}

export enum CoverageStatus {
  ACTIVE = 'ACTIVE',
  STALE = 'STALE',
  ERROR = 'ERROR',
  NOT_STARTED = 'NOT_STARTED',
}

export interface Institution {
  id: string;
  name: string;
  acronym: string;
  catalogUrl: string;
  coverageStatus: CoverageStatus;
  lastCrawled: string;
  techCount: number;
  ttoOfficeName?: string;
  missionStatement?: string;
  licensingContact?: string;
}

export interface Technology {
  id: string;
  title: string;
  institutionId: string;
  institutionName: string;
  institutionAcronym: string;
  patentNumber: string;
  abstract: string;
  licensingStatus: LicensingStatus;
  domains: TechDomain[];
  confidenceScore: number;
  provenanceLevel: ProvenanceLevel;
  sourceUrl: string;
  agentValidated: boolean;
  filingDate: string;
  inventors: string[];
  agentId?: string;
}

export interface AgentRun {
  id: string;
  agentType: 'CRAWLER' | 'VALIDATOR' | 'SUMMARIZER' | 'RANKER';
  institutionTarget: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  status: AgentStatus;
  technologiesProcessed: number;
  newDiscoveries: number;
  errorsCount: number;
  logs?: string[];
  discoveredTechIds?: string[];
}

export interface EvidenceCard {
  technology: Technology;
}

export interface Cluster {
  id: string;
  name: string;
  domain: TechDomain;
  size: number;
  institutionIds: string[];
  dominantLicensingStatus: LicensingStatus;
  averageConfidence: number;
  keyTags: string[];
  topTechnologies: Technology[];
  allTechnologyIds: string[];
}

export interface SearchMessage {
  id: string;
  type: 'user' | 'system';
  content: string;
  timestamp: string;
  agentId?: string;
  resultCount?: number;
  processingTime?: number;
  confidenceDistribution?: { range: string; count: number }[];
}

export interface CoverageStats {
  totalInstitutions: number;
  activeInstitutions: number;
  staleInstitutions: number;
  errorInstitutions: number;
  totalTechnologies: number;
  lastSyncTime: string;
}
