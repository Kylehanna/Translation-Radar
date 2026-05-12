import { Technology, ProvenanceLevel, LicensingStatus, TechDomain } from '@/lib/index';
import { Shield, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface EvidenceCardProps {
  technology: Technology;
}

interface ConfidenceGaugeProps {
  score: number;
}

interface ProvenanceBadgeProps {
  level: ProvenanceLevel;
}

interface InstitutionBadgeProps {
  acronym: string;
  fullName: string;
}

export function ConfidenceGauge({ score }: ConfidenceGaugeProps) {
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = () => {
    if (score >= 80) return 'oklch(0.55 0.18 180)';
    if (score >= 60) return 'oklch(0.62 0.14 35)';
    return 'oklch(0.55 0.20 10)';
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="48" height="48" className="-rotate-90">
        <circle
          cx="24"
          cy="24"
          r={radius}
          stroke="currentColor"
          strokeWidth="3"
          fill="none"
          className="text-muted"
        />
        <circle
          cx="24"
          cy="24"
          r={radius}
          stroke={getColor()}
          strokeWidth="3"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <span className="absolute text-xs font-mono font-semibold" style={{ color: getColor() }}>
        {score}
      </span>
    </div>
  );
}

export function ProvenanceBadge({ level }: ProvenanceBadgeProps) {
  const config = {
    [ProvenanceLevel.DIRECT_SOURCE_VERIFIED]: {
      label: 'DIRECT SOURCE VERIFIED',
      className: 'bg-chart-1/10 text-chart-1 border-chart-1/30',
    },
    [ProvenanceLevel.AGENT_VALIDATED]: {
      label: 'AGENT-VALIDATED',
      className: 'bg-accent/10 text-accent border-accent/30',
    },
    [ProvenanceLevel.NEEDS_REVIEW]: {
      label: 'NEEDS REVIEW',
      className: 'bg-destructive/10 text-destructive border-destructive/30',
    },
  };

  const { label, className } = config[level];

  return (
    <Badge variant="outline" className={`${className} text-[10px] font-mono tracking-wider px-2 py-0.5 gap-1`}>
      <Shield className="w-3 h-3" />
      {label}
    </Badge>
  );
}

export function InstitutionBadge({ acronym, fullName }: InstitutionBadgeProps) {
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-primary/5 border border-primary/20">
      <div className="w-6 h-6 rounded bg-primary/10 flex items-center justify-center">
        <span className="text-[10px] font-bold text-primary">{acronym.slice(0, 2)}</span>
      </div>
      <div className="flex flex-col">
        <span className="text-xs font-semibold text-foreground">{acronym}</span>
        <span className="text-[10px] text-muted-foreground">{fullName}</span>
      </div>
    </div>
  );
}

export function EvidenceCard({ technology }: EvidenceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getBorderColor = () => {
    if (technology.confidenceScore >= 80) return 'border-l-chart-1';
    if (technology.confidenceScore >= 60) return 'border-l-accent';
    return 'border-l-destructive';
  };

  const getLicensingBadgeColor = () => {
    switch (technology.licensingStatus) {
      case LicensingStatus.AVAILABLE:
        return 'bg-chart-1/10 text-chart-1 border-chart-1/30';
      case LicensingStatus.LICENSED:
        return 'bg-muted text-muted-foreground border-border';
      case LicensingStatus.PENDING:
        return 'bg-accent/10 text-accent border-accent/30';
      case LicensingStatus.CONTACT_TTO:
        return 'bg-primary/10 text-primary border-primary/30';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  const getDomainColor = (domain: TechDomain) => {
    const colors: Record<TechDomain, string> = {
      [TechDomain.ONCOLOGY]: 'bg-chart-1/10 text-chart-1 border-chart-1/30',
      [TechDomain.AI_ML]: 'bg-chart-3/10 text-chart-3 border-chart-3/30',
      [TechDomain.MEDICAL_IMAGING]: 'bg-chart-2/10 text-chart-2 border-chart-2/30',
      [TechDomain.BIOTECH]: 'bg-chart-4/10 text-chart-4 border-chart-4/30',
      [TechDomain.CLEANTECH]: 'bg-chart-5/10 text-chart-5 border-chart-5/30',
      [TechDomain.MEDTECH]: 'bg-accent/10 text-accent border-accent/30',
      [TechDomain.MATERIALS]: 'bg-primary/10 text-primary border-primary/30',
      [TechDomain.DIAGNOSTICS]: 'bg-chart-1/10 text-chart-1 border-chart-1/30',
      [TechDomain.THERAPEUTICS]: 'bg-chart-4/10 text-chart-4 border-chart-4/30',
      [TechDomain.DEVICES]: 'bg-chart-2/10 text-chart-2 border-chart-2/30',
    };
    return colors[domain];
  };

  return (
    <Card
      className={`p-6 border-l-4 ${getBorderColor()} transition-all duration-200 hover:shadow-lg hover:-translate-y-1 cursor-pointer`}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-foreground mb-2 leading-tight">
            {technology.title}
          </h3>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <InstitutionBadge
              acronym={technology.institutionAcronym}
              fullName={technology.institutionName}
            />
            <ProvenanceBadge level={technology.provenanceLevel} />
          </div>
        </div>
        <ConfidenceGauge score={technology.confidenceScore} />
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Badge variant="outline" className={`${getLicensingBadgeColor()} text-xs font-medium px-2 py-0.5`}>
          {technology.licensingStatus.replace(/_/g, ' ')}
        </Badge>
        {technology.domains.map((domain) => (
          <Badge
            key={domain}
            variant="outline"
            className={`${getDomainColor(domain)} text-[10px] px-2 py-0.5`}
          >
            {domain.replace(/_/g, ' ')}
          </Badge>
        ))}
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground font-medium">Patent:</span>
          <span className="font-mono text-foreground">{technology.patentNumber}</span>
        </div>

        <div className="text-sm text-muted-foreground">
          <p className={`leading-relaxed ${!isExpanded ? 'line-clamp-3' : ''}`}>
            {technology.abstract}
          </p>
          <Button
            variant="ghost"
            size="sm"
            className="mt-2 h-auto p-0 text-xs text-primary hover:text-primary/80"
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            {isExpanded ? (
              <>
                Show Less <ChevronUp className="w-3 h-3 ml-1" />
              </>
            ) : (
              <>
                Show More <ChevronDown className="w-3 h-3 ml-1" />
              </>
            )}
          </Button>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground font-medium">Source:</span>
          <a
            href={technology.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:text-primary/80 font-mono text-xs flex items-center gap-1 transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            {new URL(technology.sourceUrl).hostname}
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        {isExpanded && (
          <>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground font-medium">Filing Date:</span>
              <span className="font-mono text-foreground text-xs">{technology.filingDate}</span>
            </div>

            <div className="flex items-start gap-2 text-sm">
              <span className="text-muted-foreground font-medium">Inventors:</span>
              <span className="text-foreground text-xs">{technology.inventors.join(', ')}</span>
            </div>

            {technology.agentId && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground font-medium">Agent ID:</span>
                <span className="font-mono text-foreground text-xs">{technology.agentId}</span>
              </div>
            )}
          </>
        )}
      </div>
    </Card>
  );
}

export function EvidenceCardSkeleton() {
  return (
    <Card className="p-6 border-l-4 border-l-muted animate-pulse">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1 space-y-3">
          <div className="h-6 bg-muted rounded w-3/4" />
          <div className="flex gap-2">
            <div className="h-8 bg-muted rounded w-32" />
            <div className="h-8 bg-muted rounded w-40" />
          </div>
        </div>
        <div className="w-12 h-12 bg-muted rounded-full" />
      </div>

      <div className="flex gap-2 mb-4">
        <div className="h-6 bg-muted rounded w-24" />
        <div className="h-6 bg-muted rounded w-20" />
        <div className="h-6 bg-muted rounded w-28" />
      </div>

      <div className="space-y-3">
        <div className="h-4 bg-muted rounded w-full" />
        <div className="h-4 bg-muted rounded w-full" />
        <div className="h-4 bg-muted rounded w-2/3" />
        <div className="h-4 bg-muted rounded w-1/2" />
      </div>
    </Card>
  );
}