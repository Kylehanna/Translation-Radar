import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, CheckCircle2, AlertCircle, XCircle, Clock, ExternalLink, Filter, ArrowUpDown } from 'lucide-react';
import { INSTITUTIONS, TECHNOLOGIES, COVERAGE_STATS } from '@/data/index';
import { Institution, CoverageStatus, TechDomain } from '@/lib/index';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { InstitutionHeatmap } from '@/components/Charts';

const statusConfig = {
  [CoverageStatus.ACTIVE]: {
    icon: CheckCircle2,
    color: 'text-chart-4',
    bgColor: 'bg-chart-4/10',
    label: 'Active',
  },
  [CoverageStatus.STALE]: {
    icon: Clock,
    color: 'text-accent',
    bgColor: 'bg-accent/10',
    label: 'Stale',
  },
  [CoverageStatus.ERROR]: {
    icon: XCircle,
    color: 'text-destructive',
    bgColor: 'bg-destructive/10',
    label: 'Error',
  },
  [CoverageStatus.NOT_STARTED]: {
    icon: AlertCircle,
    color: 'text-muted-foreground',
    bgColor: 'bg-muted',
    label: 'Not Started',
  },
};

const sortOptions = [
  { value: 'name', label: 'Institution Name' },
  { value: 'coverage', label: 'Coverage Completeness' },
  { value: 'lastCrawled', label: 'Last Crawl Time' },
  { value: 'techCount', label: 'Technology Count' },
];

function formatTimestamp(timestamp: string): string {
  if (!timestamp) return 'Never';
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function InstitutionCard({ institution }: { institution: Institution }) {
  const statusInfo = statusConfig[institution.coverageStatus];
  const StatusIcon = statusInfo.icon;

  const institutionTechs = TECHNOLOGIES.filter(t => t.institutionId === institution.id);
  const domainCounts = institutionTechs.reduce((acc, tech) => {
    tech.domains.forEach(domain => {
      acc[domain] = (acc[domain] || 0) + 1;
    });
    return acc;
  }, {} as Record<TechDomain, number>);

  const topDomains = Object.entries(domainCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)
    .map(([domain]) => domain);

  const initials = institution.acronym
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="h-full hover:shadow-lg transition-shadow duration-200">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 flex-1 min-w-0">
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center text-sm font-bold text-primary-foreground flex-shrink-0"
                style={{
                  background: `linear-gradient(135deg, var(--primary) 0%, color-mix(in srgb, var(--primary) 70%, black) 100%)`,
                }}
              >
                {initials}
              </div>
              <div className="flex-1 min-w-0">
                <CardTitle className="text-base leading-tight mb-1 truncate">
                  {institution.name}
                </CardTitle>
                <p className="text-xs text-muted-foreground truncate">
                  {institution.acronym}
                </p>
              </div>
            </div>
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md ${statusInfo.bgColor} flex-shrink-0`}>
              <StatusIcon className={`w-3.5 h-3.5 ${statusInfo.color}`} />
              <span className={`text-xs font-medium ${statusInfo.color}`}>
                {statusInfo.label}
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono">{institution.techCount}</span>
            <span className="text-sm text-muted-foreground">technologies indexed</span>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Last Crawled</span>
              <span className="font-mono font-medium">{formatTimestamp(institution.lastCrawled)}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Catalog URL</span>
              <a
                href={institution.catalogUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-primary hover:underline"
              >
                <span>View</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {topDomains.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">Top Domains</p>
              <div className="flex flex-wrap gap-1.5">
                {topDomains.map(domain => (
                  <Badge key={domain} variant="secondary" className="text-xs px-2 py-0.5">
                    {domain.replace(/_/g, ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => (window.location.hash = `/catalogs?institution=${institution.id}`)}
          >
            View Catalog
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: number;
  color: string;
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
            <Icon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold font-mono">{value}</p>
            <p className="text-sm text-muted-foreground">{label}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function CoverageMap() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('name');

  const filteredAndSortedInstitutions = useMemo(() => {
    let filtered = INSTITUTIONS;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        inst =>
          inst.name.toLowerCase().includes(query) ||
          inst.acronym.toLowerCase().includes(query)
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(inst => inst.coverageStatus === statusFilter);
    }

    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'coverage':
          return b.techCount - a.techCount;
        case 'lastCrawled':
          if (!a.lastCrawled) return 1;
          if (!b.lastCrawled) return -1;
          return new Date(b.lastCrawled).getTime() - new Date(a.lastCrawled).getTime();
        case 'techCount':
          return b.techCount - a.techCount;
        default:
          return 0;
      }
    });

    return sorted;
  }, [searchQuery, statusFilter, sortBy]);

  const coveragePercentage = Math.round(
    (COVERAGE_STATS.activeInstitutions / COVERAGE_STATS.totalInstitutions) * 100
  );

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-[1800px] mx-auto p-6 space-y-6">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold tracking-tight uppercase">INSTITUTION COVERAGE MAP</h1>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
              <span className="font-mono">LIVE</span>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>
              <span className="font-mono font-semibold text-foreground">
                {COVERAGE_STATS.activeInstitutions}
              </span>{' '}
              of{' '}
              <span className="font-mono font-semibold text-foreground">
                {COVERAGE_STATS.totalInstitutions}
              </span>{' '}
              institutions indexed
            </span>
            <span className="text-border">•</span>
            <span>
              <span className="font-mono font-semibold text-foreground">{coveragePercentage}%</span>{' '}
              coverage
            </span>
            <span className="text-border">•</span>
            <span>
              Last sync:{' '}
              <span className="font-mono font-semibold text-foreground">
                {formatTimestamp(COVERAGE_STATS.lastSyncTime)}
              </span>
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            icon={CheckCircle2}
            label="Total Institutions"
            value={COVERAGE_STATS.totalInstitutions}
            color="bg-primary/10 text-primary"
          />
          <MetricCard
            icon={CheckCircle2}
            label="Active Coverage"
            value={COVERAGE_STATS.activeInstitutions}
            color="bg-chart-4/10 text-chart-4"
          />
          <MetricCard
            icon={Clock}
            label="Stale Coverage"
            value={COVERAGE_STATS.staleInstitutions}
            color="bg-accent/10 text-accent"
          />
          <MetricCard
            icon={XCircle}
            label="Error Count"
            value={COVERAGE_STATS.errorInstitutions}
            color="bg-destructive/10 text-destructive"
          />
        </div>

        <Card>
          <CardContent className="pt-6">
            <InstitutionHeatmap institutions={INSTITUTIONS} technologies={TECHNOLOGIES} />
          </CardContent>
        </Card>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search institutions..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-[180px]">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value={CoverageStatus.ACTIVE}>Active</SelectItem>
              <SelectItem value={CoverageStatus.STALE}>Stale</SelectItem>
              <SelectItem value={CoverageStatus.ERROR}>Error</SelectItem>
              <SelectItem value={CoverageStatus.NOT_STARTED}>Not Started</SelectItem>
            </SelectContent>
          </Select>
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-full sm:w-[200px]">
              <ArrowUpDown className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              {sortOptions.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: {
                staggerChildren: 0.05,
              },
            },
          }}
        >
          {filteredAndSortedInstitutions.map(institution => (
            <InstitutionCard key={institution.id} institution={institution} />
          ))}
        </motion.div>

        {filteredAndSortedInstitutions.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium mb-1">No institutions found</p>
              <p className="text-sm text-muted-foreground">
                Try adjusting your search or filter criteria
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
