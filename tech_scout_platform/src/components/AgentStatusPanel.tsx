import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Play, Pause, Activity, CheckCircle2, AlertCircle, Clock, Loader2 } from 'lucide-react';
import { AgentStatus } from '@/lib/index';
import { AGENT_RUNS, COVERAGE_STATS } from '@/data/index';

interface AgentStatusBadgeProps {
  status: AgentStatus;
  size?: 'sm' | 'md';
}

export function AgentStatusBadge({ status, size = 'md' }: AgentStatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case AgentStatus.CRAWLING:
        return {
          label: 'CRAWLING',
          color: 'bg-accent text-accent-foreground',
          icon: Activity,
          pulse: true,
        };
      case AgentStatus.VALIDATING:
        return {
          label: 'VALIDATING',
          color: 'bg-chart-1 text-primary-foreground',
          icon: CheckCircle2,
          pulse: true,
        };
      case AgentStatus.SUMMARIZING:
        return {
          label: 'SUMMARIZING',
          color: 'bg-chart-1 text-primary-foreground',
          icon: Loader2,
          pulse: true,
        };
      case AgentStatus.IDLE:
        return {
          label: 'IDLE',
          color: 'bg-muted text-muted-foreground',
          icon: Clock,
          pulse: false,
        };
      case AgentStatus.ERROR:
        return {
          label: 'ERROR',
          color: 'bg-destructive text-destructive-foreground',
          icon: AlertCircle,
          pulse: false,
        };
      case AgentStatus.COMPLETED:
        return {
          label: 'COMPLETED',
          color: 'bg-chart-4 text-primary-foreground',
          icon: CheckCircle2,
          pulse: false,
        };
      case AgentStatus.RUNNING:
        return {
          label: 'RUNNING',
          color: 'bg-accent text-accent-foreground',
          icon: Activity,
          pulse: true,
        };
      case AgentStatus.QUEUED:
        return {
          label: 'QUEUED',
          color: 'bg-secondary text-secondary-foreground',
          icon: Clock,
          pulse: false,
        };
      case AgentStatus.FAILED:
        return {
          label: 'FAILED',
          color: 'bg-destructive text-destructive-foreground',
          icon: AlertCircle,
          pulse: false,
        };
      default:
        return {
          label: 'UNKNOWN',
          color: 'bg-muted text-muted-foreground',
          icon: Clock,
          pulse: false,
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <Badge className={`${config.color} ${sizeClass} font-mono font-medium inline-flex items-center gap-1.5 relative`}>
      {config.pulse && (
        <span className="absolute inset-0 rounded-md animate-pulse opacity-50" style={{ backgroundColor: 'currentColor' }} />
      )}
      <Icon className={size === 'sm' ? 'h-3 w-3' : 'h-3.5 w-3.5'} />
      <span className="relative z-10">{config.label}</span>
    </Badge>
  );
}

interface AgentStatusPanelProps {
  className?: string;
}

export function AgentStatusPanel({ className = '' }: AgentStatusPanelProps) {
  const [isRunning, setIsRunning] = useState(true);

  const activeRuns = AGENT_RUNS.filter(
    run => run.status === AgentStatus.RUNNING || run.status === AgentStatus.CRAWLING || run.status === AgentStatus.VALIDATING || run.status === AgentStatus.SUMMARIZING
  ).slice(0, 3);

  const recentRuns = AGENT_RUNS.filter(
    run => run.status === AgentStatus.COMPLETED || run.status === AgentStatus.FAILED
  ).slice(0, 2);

  const mockActiveAgents = [
    {
      id: 'agent-crawler-01',
      task: 'Crawling MIT TLO catalog',
      status: AgentStatus.CRAWLING,
      progress: 78,
      institution: 'MIT',
      lastAction: '2 min ago',
    },
    {
      id: 'agent-validator-01',
      task: 'Validating Stanford records',
      status: AgentStatus.VALIDATING,
      progress: 45,
      institution: 'Stanford',
      lastAction: '5 min ago',
    },
    {
      id: 'agent-summarizer-02',
      task: 'Summarizing abstracts',
      status: AgentStatus.SUMMARIZING,
      progress: 92,
      institution: 'Multiple',
      lastAction: '1 min ago',
    },
  ];

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hr ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-sidebar-foreground">Agent Control</h3>
          {isRunning && (
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
              </span>
              <span className="text-xs font-mono text-accent uppercase">Live</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Button
            onClick={() => setIsRunning(!isRunning)}
            className="bg-accent hover:bg-accent/90 text-accent-foreground font-medium text-xs h-9"
          >
            <Play className="h-3.5 w-3.5 mr-1.5" />
            Start New Run
          </Button>
          <Button
            onClick={() => setIsRunning(!isRunning)}
            variant="outline"
            className="border-sidebar-border text-sidebar-foreground hover:bg-sidebar-accent font-medium text-xs h-9"
          >
            <Pause className="h-3.5 w-3.5 mr-1.5" />
            Pause All
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/70">Active Agents</h4>
        <div className="space-y-3">
          {mockActiveAgents.map((agent) => (
            <div
              key={agent.id}
              className="bg-sidebar-accent/50 rounded-lg p-3 space-y-2.5 border border-sidebar-border/50"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="font-mono text-xs text-sidebar-foreground/90 mb-1">{agent.id}</div>
                  <div className="text-xs text-sidebar-foreground/70 truncate">{agent.task}</div>
                </div>
                <AgentStatusBadge status={agent.status} size="sm" />
              </div>
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-sidebar-foreground/60">Progress</span>
                  <span className="font-mono text-sidebar-foreground">{agent.progress}%</span>
                </div>
                <Progress value={agent.progress} className="h-1.5" />
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-sidebar-foreground/60">Institution:</span>
                <span className="font-medium text-sidebar-foreground">{agent.institution}</span>
              </div>
              <div className="text-xs text-sidebar-foreground/50 font-mono">{agent.lastAction}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-3 pt-4 border-t border-sidebar-border">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/70">Global Stats</h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-sidebar-accent/30 rounded-lg p-3 border border-sidebar-border/30">
            <div className="text-2xl font-bold text-sidebar-foreground font-mono">{COVERAGE_STATS.totalTechnologies.toLocaleString()}</div>
            <div className="text-xs text-sidebar-foreground/60 mt-1">Inventions Indexed</div>
          </div>
          <div className="bg-sidebar-accent/30 rounded-lg p-3 border border-sidebar-border/30">
            <div className="text-2xl font-bold text-sidebar-foreground font-mono">{COVERAGE_STATS.activeInstitutions}</div>
            <div className="text-xs text-sidebar-foreground/60 mt-1">Institutions Covered</div>
          </div>
        </div>
        <div className="bg-sidebar-accent/30 rounded-lg p-3 border border-sidebar-border/30">
          <div className="text-xs text-sidebar-foreground/60 mb-1">Last Full Sweep</div>
          <div className="text-sm font-mono text-sidebar-foreground">{formatTimestamp(COVERAGE_STATS.lastSyncTime)}</div>
        </div>
      </div>

      {recentRuns.length > 0 && (
        <div className="space-y-3 pt-4 border-t border-sidebar-border">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/70">Recent Runs</h4>
          <div className="space-y-2">
            {recentRuns.map((run) => (
              <div
                key={run.id}
                className="bg-sidebar-accent/20 rounded-lg p-2.5 border border-sidebar-border/20"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono text-xs text-sidebar-foreground/90">{run.agentType}</span>
                  <AgentStatusBadge status={run.status} size="sm" />
                </div>
                <div className="text-xs text-sidebar-foreground/60">{run.institutionTarget}</div>
                <div className="text-xs text-sidebar-foreground/50 font-mono mt-1">{formatTimestamp(run.startTime)}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
