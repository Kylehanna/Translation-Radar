import { ReactNode, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { ROUTE_PATHS, CoverageStatus } from '@/lib/index';
import { INSTITUTIONS, COVERAGE_STATS } from '@/data/index';
import {
  Search,
  Map,
  BookOpen,
  Activity,
  Layers,
  User,
  ChevronRight,
  Circle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface LayoutProps {
  children: ReactNode;
}

const NAV_ITEMS = [
  { path: ROUTE_PATHS.SEARCH, label: 'Search', icon: Search },
  { path: ROUTE_PATHS.COVERAGE, label: 'Coverage Map', icon: Map },
  { path: ROUTE_PATHS.CATALOGS, label: 'Catalogs', icon: BookOpen },
  { path: ROUTE_PATHS.AGENT_RUNS, label: 'Agent Runs', icon: Activity },
  { path: ROUTE_PATHS.CLUSTERS, label: 'Clusters', icon: Layers },
];

const getCoverageStatusColor = (status: CoverageStatus) => {
  switch (status) {
    case CoverageStatus.ACTIVE:
      return 'bg-chart-1';
    case CoverageStatus.STALE:
      return 'bg-accent';
    case CoverageStatus.ERROR:
      return 'bg-destructive';
    case CoverageStatus.NOT_STARTED:
      return 'bg-muted-foreground';
    default:
      return 'bg-muted-foreground';
  }
};

const formatTimestamp = (timestamp: string) => {
  if (!timestamp) return 'Never';
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
};

export function TopHeader() {
  const activeAgents = 3;
  const lastSync = formatTimestamp(COVERAGE_STATS.lastSyncTime);

  return (
    <header className="fixed top-0 left-0 right-0 h-12 bg-sidebar border-b border-sidebar-border z-50 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h1 className="text-sidebar-foreground font-mono text-sm font-semibold tracking-wider">
          SCOUT COMMAND
        </h1>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            <span className="text-xs text-sidebar-foreground/70 font-mono">LIVE</span>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-6 text-xs text-sidebar-foreground/70 font-mono">
        <div className="flex items-center gap-2">
          <span className="text-sidebar-foreground/50">AGENTS:</span>
          <span className="text-accent font-semibold">{activeAgents}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sidebar-foreground/50">INSTITUTIONS:</span>
          <span className="text-sidebar-foreground">{COVERAGE_STATS.activeInstitutions}/{COVERAGE_STATS.totalInstitutions}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sidebar-foreground/50">LAST SYNC:</span>
          <span className="text-sidebar-foreground">{lastSync}</span>
        </div>
        <button className="w-8 h-8 rounded-full bg-sidebar-accent flex items-center justify-center hover:bg-sidebar-accent/80 transition-colors">
          <User className="w-4 h-4 text-sidebar-foreground" />
        </button>
      </div>
    </header>
  );
}

export function LeftRail() {
  const location = useLocation();
  const [expandedSection, setExpandedSection] = useState<string>('institutions');

  return (
    <aside className="fixed left-0 top-12 bottom-0 w-[280px] bg-sidebar border-r border-sidebar-border overflow-y-auto">
      <nav className="p-4 space-y-1 border-b border-sidebar-border">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-foreground'
                  : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
              )}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4">
        <button
          onClick={() => setExpandedSection(expandedSection === 'institutions' ? '' : 'institutions')}
          className="w-full flex items-center justify-between text-xs font-semibold text-sidebar-foreground/50 uppercase tracking-wider mb-3 hover:text-sidebar-foreground/70 transition-colors"
        >
          <span>Institution Coverage</span>
          <ChevronRight
            className={cn(
              'w-3 h-3 transition-transform',
              expandedSection === 'institutions' && 'rotate-90'
            )}
          />
        </button>
        
        {expandedSection === 'institutions' && (
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {INSTITUTIONS.slice(0, 15).map((institution) => (
              <div
                key={institution.id}
                className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-sidebar-accent/30 transition-colors cursor-pointer"
              >
                <Circle
                  className={cn(
                    'w-2 h-2 fill-current',
                    getCoverageStatusColor(institution.coverageStatus)
                  )}
                />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-sidebar-foreground truncate">
                    {institution.acronym}
                  </div>
                  <div className="text-[10px] text-sidebar-foreground/50 font-mono">
                    {institution.techCount} techs
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="p-4 border-t border-sidebar-border">
        <div className="text-xs font-semibold text-sidebar-foreground/50 uppercase tracking-wider mb-3">
          System Status
        </div>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-sidebar-foreground/70">Total Technologies</span>
            <span className="text-sidebar-foreground font-mono">{COVERAGE_STATS.totalTechnologies.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sidebar-foreground/70">Active Coverage</span>
            <span className="text-chart-1 font-mono">{COVERAGE_STATS.activeInstitutions}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sidebar-foreground/70">Stale Coverage</span>
            <span className="text-accent font-mono">{COVERAGE_STATS.staleInstitutions}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sidebar-foreground/70">Errors</span>
            <span className="text-destructive font-mono">{COVERAGE_STATS.errorInstitutions}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <TopHeader />
      <LeftRail />
      <main className="ml-[280px] pt-12">
        <div className="w-full">
          {children}
        </div>
      </main>
    </div>
  );
}
