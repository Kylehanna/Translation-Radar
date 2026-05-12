import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, Play, Pause, Calendar, Clock, CheckCircle2, XCircle, Loader2, AlertCircle } from 'lucide-react';
import { AGENT_RUNS, INSTITUTIONS, TECHNOLOGIES } from '@/data/index';
import { AgentRun, AgentStatus } from '@/lib/index';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';

const getStatusColor = (status: AgentStatus) => {
  switch (status) {
    case AgentStatus.COMPLETED:
      return 'bg-chart-1/20 text-chart-1 border-chart-1/30';
    case AgentStatus.RUNNING:
      return 'bg-accent/20 text-accent border-accent/30';
    case AgentStatus.FAILED:
    case AgentStatus.ERROR:
      return 'bg-destructive/20 text-destructive border-destructive/30';
    case AgentStatus.QUEUED:
      return 'bg-muted text-muted-foreground border-border';
    default:
      return 'bg-muted text-muted-foreground border-border';
  }
};

const getStatusIcon = (status: AgentStatus) => {
  switch (status) {
    case AgentStatus.COMPLETED:
      return <CheckCircle2 className="w-4 h-4" />;
    case AgentStatus.RUNNING:
      return <Loader2 className="w-4 h-4 animate-spin" />;
    case AgentStatus.FAILED:
    case AgentStatus.ERROR:
      return <XCircle className="w-4 h-4" />;
    case AgentStatus.QUEUED:
      return <Clock className="w-4 h-4" />;
    default:
      return <AlertCircle className="w-4 h-4" />;
  }
};

const formatDuration = (minutes: number | undefined) => {
  if (!minutes) return 'N/A';
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const RunQueueItem = ({ run }: { run: AgentRun }) => {
  const progress = run.status === AgentStatus.RUNNING ? 65 : 0;
  
  return (
    <Card className="p-4 border-l-4 border-l-accent">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <div>
            <div className="font-mono text-sm text-foreground">{run.id}</div>
            <div className="text-xs text-muted-foreground mt-0.5">
              {run.agentType} • {run.institutionTarget}
            </div>
          </div>
        </div>
        <Badge variant="outline" className={getStatusColor(run.status)}>
          <span className="flex items-center gap-1.5">
            {getStatusIcon(run.status)}
            {run.status}
          </span>
        </Badge>
      </div>
      {run.status === AgentStatus.RUNNING && (
        <div className="space-y-2">
          <Progress value={progress} className="h-1.5" />
          <div className="text-xs text-muted-foreground">
            Processing: {run.technologiesProcessed} technologies
          </div>
        </div>
      )}
    </Card>
  );
};

const RunDetailPanel = ({ run }: { run: AgentRun }) => {
  const discoveredTechs = TECHNOLOGIES.filter(t => run.discoveredTechIds?.includes(t.id));
  
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className="border-t border-border mt-4 pt-4"
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-semibold mb-3 uppercase tracking-wide">Execution Log</h4>
          <div className="bg-sidebar rounded-lg p-4 max-h-80 overflow-y-auto">
            <div className="font-mono text-xs space-y-1">
              {run.logs?.map((log, idx) => (
                <div key={idx} className="text-sidebar-foreground/80">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div>
          <h4 className="text-sm font-semibold mb-3 uppercase tracking-wide">Discovered Technologies</h4>
          {discoveredTechs.length > 0 ? (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {discoveredTechs.map(tech => (
                <Card key={tech.id} className="p-3">
                  <div className="text-sm font-medium mb-1">{tech.title}</div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span className="font-mono">{tech.patentNumber}</span>
                    <span>•</span>
                    <span>{tech.institutionAcronym}</span>
                    <span>•</span>
                    <Badge variant="outline" className="text-xs">
                      {tech.confidenceScore}% confidence
                    </Badge>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground italic">No new discoveries in this run</div>
          )}
          
          {run.errorsCount > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold mb-2 uppercase tracking-wide text-destructive">Errors</h4>
              <Card className="p-3 border-destructive/30 bg-destructive/5">
                <div className="text-sm text-destructive">
                  {run.errorsCount} error{run.errorsCount > 1 ? 's' : ''} encountered during execution
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

const ScheduleRunDialog = () => {
  const [selectedInstitutions, setSelectedInstitutions] = useState<string[]>([]);
  const [agentType, setAgentType] = useState<string>('CRAWLER');
  const [confidenceThreshold, setConfidenceThreshold] = useState([70]);
  
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className="bg-accent text-accent-foreground hover:bg-accent/90">
          <Play className="w-4 h-4 mr-2" />
          Schedule New Run
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold uppercase tracking-wide">Schedule Agent Run</DialogTitle>
        </DialogHeader>
        <div className="space-y-6 py-4">
          <div>
            <Label className="text-sm font-semibold mb-3 block uppercase tracking-wide">Agent Type</Label>
            <Select value={agentType} onValueChange={setAgentType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="CRAWLER">CRAWLER</SelectItem>
                <SelectItem value="VALIDATOR">VALIDATOR</SelectItem>
                <SelectItem value="SUMMARIZER">SUMMARIZER</SelectItem>
                <SelectItem value="RANKER">RANKER</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label className="text-sm font-semibold mb-3 block uppercase tracking-wide">Target Institutions</Label>
            <div className="grid grid-cols-2 gap-3 max-h-60 overflow-y-auto p-1">
              {INSTITUTIONS.map(inst => (
                <div key={inst.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={inst.id}
                    checked={selectedInstitutions.includes(inst.id)}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        setSelectedInstitutions([...selectedInstitutions, inst.id]);
                      } else {
                        setSelectedInstitutions(selectedInstitutions.filter(id => id !== inst.id));
                      }
                    }}
                  />
                  <label
                    htmlFor={inst.id}
                    className="text-sm cursor-pointer"
                  >
                    {inst.acronym}
                  </label>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <Label className="text-sm font-semibold mb-3 block uppercase tracking-wide">
              Confidence Threshold: {confidenceThreshold[0]}%
            </Label>
            <Slider
              value={confidenceThreshold}
              onValueChange={setConfidenceThreshold}
              min={0}
              max={100}
              step={5}
              className="w-full"
            />
          </div>
          
          <Button className="w-full bg-accent text-accent-foreground hover:bg-accent/90">
            <Play className="w-4 h-4 mr-2" />
            Start Run
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default function AgentRuns() {
  const [expandedRun, setExpandedRun] = useState<string | null>(null);
  const [filterAgentType, setFilterAgentType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterInstitution, setFilterInstitution] = useState<string>('all');
  
  const activeRuns = AGENT_RUNS.filter(r => r.status === AgentStatus.RUNNING || r.status === AgentStatus.QUEUED);
  
  const filteredRuns = AGENT_RUNS.filter(run => {
    if (filterAgentType !== 'all' && run.agentType !== filterAgentType) return false;
    if (filterStatus !== 'all' && run.status !== filterStatus) return false;
    if (filterInstitution !== 'all' && run.institutionTarget !== filterInstitution) return false;
    return true;
  });
  
  const totalRuns = AGENT_RUNS.length;
  const completedRuns = AGENT_RUNS.filter(r => r.status === AgentStatus.COMPLETED).length;
  const successRate = Math.round((completedRuns / totalRuns) * 100);
  const avgDuration = Math.round(
    AGENT_RUNS.filter(r => r.duration).reduce((sum, r) => sum + (r.duration || 0), 0) / 
    AGENT_RUNS.filter(r => r.duration).length
  );
  const weeklyDiscoveries = AGENT_RUNS.reduce((sum, r) => sum + r.newDiscoveries, 0);
  
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold uppercase tracking-tight mb-2">Agent Runs</h1>
          <p className="text-muted-foreground">Audit log and execution history of all AI agent operations</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-4">
            <div className="text-sm text-muted-foreground uppercase tracking-wide mb-1">Total Runs</div>
            <div className="text-3xl font-bold font-mono">{totalRuns}</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground uppercase tracking-wide mb-1">Success Rate</div>
            <div className="text-3xl font-bold font-mono text-chart-1">{successRate}%</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground uppercase tracking-wide mb-1">Avg Duration</div>
            <div className="text-3xl font-bold font-mono">{avgDuration}m</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground uppercase tracking-wide mb-1">Weekly Discoveries</div>
            <div className="text-3xl font-bold font-mono text-accent">{weeklyDiscoveries}</div>
          </Card>
        </div>
        
        {activeRuns.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold uppercase tracking-wide">Run Queue</h2>
              <Badge variant="outline" className="bg-accent/20 text-accent border-accent/30">
                {activeRuns.length} Active
              </Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeRuns.map(run => (
                <RunQueueItem key={run.id} run={run} />
              ))}
            </div>
          </div>
        )}
        
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold uppercase tracking-wide">Execution History</h2>
            <ScheduleRunDialog />
          </div>
          
          <div className="flex flex-wrap gap-3 mb-6">
            <Select value={filterAgentType} onValueChange={setFilterAgentType}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Agent Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Agent Types</SelectItem>
                <SelectItem value="CRAWLER">CRAWLER</SelectItem>
                <SelectItem value="VALIDATOR">VALIDATOR</SelectItem>
                <SelectItem value="SUMMARIZER">SUMMARIZER</SelectItem>
                <SelectItem value="RANKER">RANKER</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value={AgentStatus.COMPLETED}>COMPLETED</SelectItem>
                <SelectItem value={AgentStatus.RUNNING}>RUNNING</SelectItem>
                <SelectItem value={AgentStatus.FAILED}>FAILED</SelectItem>
                <SelectItem value={AgentStatus.QUEUED}>QUEUED</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterInstitution} onValueChange={setFilterInstitution}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Institution" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Institutions</SelectItem>
                {Array.from(new Set(AGENT_RUNS.map(r => r.institutionTarget))).map(inst => (
                  <SelectItem key={inst} value={inst}>{inst}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <div className="space-y-3">
          {filteredRuns.map(run => (
            <Card key={run.id} className="overflow-hidden">
              <div
                className="p-5 cursor-pointer hover:bg-muted/30 transition-colors"
                onClick={() => setExpandedRun(expandedRun === run.id ? null : run.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="mt-1">
                      {expandedRun === run.id ? (
                        <ChevronDown className="w-5 h-5 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-mono text-sm font-semibold">{run.id}</span>
                        <Badge variant="outline" className="text-xs">{run.agentType}</Badge>
                        <Badge variant="outline" className={getStatusColor(run.status)}>
                          <span className="flex items-center gap-1.5">
                            {getStatusIcon(run.status)}
                            {run.status}
                          </span>
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                        <div>
                          <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Institution</div>
                          <div className="font-medium">{run.institutionTarget}</div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Start Time</div>
                          <div className="font-mono text-xs">{formatTimestamp(run.startTime)}</div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Duration</div>
                          <div className="font-mono text-xs">{formatDuration(run.duration)}</div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Processed</div>
                          <div className="font-mono text-xs">{run.technologiesProcessed}</div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Discoveries</div>
                          <div className="font-mono text-xs text-accent">{run.newDiscoveries}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {run.errorsCount > 0 && (
                    <Badge variant="outline" className="bg-destructive/20 text-destructive border-destructive/30">
                      {run.errorsCount} error{run.errorsCount > 1 ? 's' : ''}
                    </Badge>
                  )}
                </div>
              </div>
              
              <AnimatePresence>
                {expandedRun === run.id && <RunDetailPanel run={run} />}
              </AnimatePresence>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}