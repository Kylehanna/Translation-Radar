import { TechDomain, Technology, Institution } from '@/lib/index';
import { TECHNOLOGIES, INSTITUTIONS } from '@/data/index';
import { motion } from 'framer-motion';
import { useMemo } from 'react';

interface DomainDistributionChartProps {
  technologies?: Technology[];
}

export function DomainDistributionChart({ technologies = TECHNOLOGIES }: DomainDistributionChartProps) {
  const domainCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    technologies.forEach(tech => {
      tech.domains.forEach(domain => {
        counts[domain] = (counts[domain] || 0) + 1;
      });
    });
    return Object.entries(counts)
      .map(([domain, count]) => ({ domain, count }))
      .sort((a, b) => b.count - a.count);
  }, [technologies]);

  const maxCount = Math.max(...domainCounts.map(d => d.count));

  const domainLabels: Record<string, string> = {
    [TechDomain.ONCOLOGY]: 'Oncology',
    [TechDomain.AI_ML]: 'AI/ML',
    [TechDomain.MEDICAL_IMAGING]: 'Medical Imaging',
    [TechDomain.BIOTECH]: 'Biotech',
    [TechDomain.CLEANTECH]: 'Cleantech',
    [TechDomain.MEDTECH]: 'Medtech',
    [TechDomain.MATERIALS]: 'Materials',
    [TechDomain.DIAGNOSTICS]: 'Diagnostics',
    [TechDomain.THERAPEUTICS]: 'Therapeutics',
    [TechDomain.DEVICES]: 'Devices',
  };

  const domainColors: Record<string, string> = {
    [TechDomain.ONCOLOGY]: 'bg-chart-1',
    [TechDomain.AI_ML]: 'bg-chart-2',
    [TechDomain.MEDICAL_IMAGING]: 'bg-chart-3',
    [TechDomain.BIOTECH]: 'bg-chart-4',
    [TechDomain.CLEANTECH]: 'bg-chart-5',
    [TechDomain.MEDTECH]: 'bg-accent',
    [TechDomain.MATERIALS]: 'bg-primary',
    [TechDomain.DIAGNOSTICS]: 'bg-chart-1',
    [TechDomain.THERAPEUTICS]: 'bg-chart-4',
    [TechDomain.DEVICES]: 'bg-chart-3',
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">Technology Domains</h3>
        <span className="text-xs font-mono text-muted-foreground">{technologies.length} total</span>
      </div>
      <div className="space-y-2">
        {domainCounts.map(({ domain, count }, index) => (
          <motion.div
            key={domain}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="flex items-center gap-3"
          >
            <div className="w-32 text-xs font-medium text-foreground truncate">
              {domainLabels[domain as TechDomain] || domain}
            </div>
            <div className="flex-1 h-8 bg-muted rounded-sm overflow-hidden relative">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(count / maxCount) * 100}%` }}
                transition={{ duration: 0.6, delay: index * 0.05 }}
                className={`h-full ${domainColors[domain as TechDomain] || 'bg-accent'} flex items-center justify-end pr-2`}
              >
                <span className="text-xs font-mono font-semibold text-white">{count}</span>
              </motion.div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

interface ConfidenceHistogramProps {
  technologies?: Technology[];
}

export function ConfidenceHistogram({ technologies = TECHNOLOGIES }: ConfidenceHistogramProps) {
  const buckets = useMemo(() => {
    const bucketData: { range: string; count: number; color: string }[] = [
      { range: '0-10', count: 0, color: 'bg-destructive' },
      { range: '10-20', count: 0, color: 'bg-destructive' },
      { range: '20-30', count: 0, color: 'bg-destructive/80' },
      { range: '30-40', count: 0, color: 'bg-destructive/60' },
      { range: '40-50', count: 0, color: 'bg-muted-foreground' },
      { range: '50-60', count: 0, color: 'bg-muted-foreground' },
      { range: '60-70', count: 0, color: 'bg-accent/60' },
      { range: '70-80', count: 0, color: 'bg-accent/80' },
      { range: '80-90', count: 0, color: 'bg-accent' },
      { range: '90-100', count: 0, color: 'bg-chart-4' },
    ];

    technologies.forEach(tech => {
      const bucketIndex = Math.min(Math.floor(tech.confidenceScore / 10), 9);
      bucketData[bucketIndex].count++;
    });

    return bucketData;
  }, [technologies]);

  const maxCount = Math.max(...buckets.map(b => b.count));

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">Confidence Distribution</h3>
        <span className="text-xs font-mono text-muted-foreground">{technologies.length} records</span>
      </div>
      <div className="flex items-end justify-between gap-1 h-32">
        {buckets.map((bucket, index) => (
          <motion.div
            key={bucket.range}
            initial={{ height: 0 }}
            animate={{ height: maxCount > 0 ? `${(bucket.count / maxCount) * 100}%` : '0%' }}
            transition={{ duration: 0.5, delay: index * 0.05 }}
            className="flex-1 relative group"
          >
            <div className={`w-full h-full ${bucket.color} rounded-t-sm transition-all hover:opacity-80`}>
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-xs font-mono font-semibold text-white">{bucket.count}</span>
              </div>
            </div>
            <div className="absolute -bottom-5 left-0 right-0 text-center">
              <span className="text-[10px] font-mono text-muted-foreground">{bucket.range.split('-')[0]}</span>
            </div>
          </motion.div>
        ))}
      </div>
      <div className="pt-4 flex justify-between text-[10px] font-mono text-muted-foreground">
        <span>Low Confidence</span>
        <span>High Confidence</span>
      </div>
    </div>
  );
}

interface ClusterForceGraphProps {
  technologies: Technology[];
  clusterName: string;
}

export function ClusterForceGraph({ technologies, clusterName }: ClusterForceGraphProps) {
  const nodes = useMemo(() => {
    const domainGroups: Record<string, Technology[]> = {};
    technologies.forEach(tech => {
      const primaryDomain = tech.domains[0];
      if (!domainGroups[primaryDomain]) {
        domainGroups[primaryDomain] = [];
      }
      domainGroups[primaryDomain].push(tech);
    });

    const nodeData: Array<{
      id: string;
      x: number;
      y: number;
      size: number;
      color: string;
      tech: Technology;
    }> = [];

    const domainColors: Record<string, string> = {
      [TechDomain.ONCOLOGY]: '#55b4d4',
      [TechDomain.AI_ML]: '#d97706',
      [TechDomain.MEDICAL_IMAGING]: '#8b5cf6',
      [TechDomain.BIOTECH]: '#10b981',
      [TechDomain.CLEANTECH]: '#f59e0b',
      [TechDomain.MEDTECH]: '#d97706',
      [TechDomain.MATERIALS]: '#3b82f6',
      [TechDomain.DIAGNOSTICS]: '#55b4d4',
      [TechDomain.THERAPEUTICS]: '#10b981',
      [TechDomain.DEVICES]: '#8b5cf6',
    };

    const centerX = 200;
    const centerY = 150;
    const clusterRadius = 80;

    Object.entries(domainGroups).forEach(([domain, techs], groupIndex) => {
      const angle = (groupIndex / Object.keys(domainGroups).length) * 2 * Math.PI;
      const groupCenterX = centerX + Math.cos(angle) * clusterRadius;
      const groupCenterY = centerY + Math.sin(angle) * clusterRadius;

      techs.forEach((tech, techIndex) => {
        const localAngle = (techIndex / techs.length) * 2 * Math.PI;
        const localRadius = 20 + Math.random() * 15;
        const x = groupCenterX + Math.cos(localAngle) * localRadius;
        const y = groupCenterY + Math.sin(localAngle) * localRadius;

        nodeData.push({
          id: tech.id,
          x,
          y,
          size: 4 + (tech.confidenceScore / 100) * 8,
          color: domainColors[domain as TechDomain] || '#d97706',
          tech,
        });
      });
    });

    return nodeData;
  }, [technologies]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">{clusterName}</h3>
        <span className="text-xs font-mono text-muted-foreground">{technologies.length} technologies</span>
      </div>
      <div className="bg-card border border-border rounded-lg p-4">
        <svg width="100%" height="300" viewBox="0 0 400 300" className="overflow-visible">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          {nodes.map((node, index) => (
            <motion.g key={node.id}>
              <motion.line
                x1={200}
                y1={150}
                x2={node.x}
                y2={node.y}
                stroke="currentColor"
                strokeWidth="0.5"
                className="text-border"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.2 }}
                transition={{ duration: 0.8, delay: index * 0.02 }}
              />
              <motion.circle
                cx={node.x}
                cy={node.y}
                r={node.size}
                fill={node.color}
                filter="url(#glow)"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 0.9 }}
                transition={{ duration: 0.5, delay: index * 0.02 }}
                whileHover={{ scale: 1.5, opacity: 1 }}
                className="cursor-pointer"
              >
                <title>{node.tech.title} - {node.tech.confidenceScore}%</title>
              </motion.circle>
            </motion.g>
          ))}
        </svg>
      </div>
    </div>
  );
}

interface InstitutionHeatmapProps {
  institutions?: Institution[];
  technologies?: Technology[];
}

export function InstitutionHeatmap({ institutions = INSTITUTIONS.slice(0, 12), technologies = TECHNOLOGIES }: InstitutionHeatmapProps) {
  const domains = [
    TechDomain.ONCOLOGY,
    TechDomain.AI_ML,
    TechDomain.BIOTECH,
    TechDomain.CLEANTECH,
    TechDomain.MEDTECH,
    TechDomain.MATERIALS,
  ];

  const domainLabels: Record<string, string> = {
    [TechDomain.ONCOLOGY]: 'Onco',
    [TechDomain.AI_ML]: 'AI/ML',
    [TechDomain.BIOTECH]: 'Biotech',
    [TechDomain.CLEANTECH]: 'Clean',
    [TechDomain.MEDTECH]: 'Med',
    [TechDomain.MATERIALS]: 'Mat',
  };

  const heatmapData = useMemo(() => {
    const data: Record<string, Record<string, number>> = {};

    institutions.forEach(inst => {
      data[inst.id] = {};
      domains.forEach(domain => {
        data[inst.id][domain] = 0;
      });
    });

    technologies.forEach(tech => {
      if (data[tech.institutionId]) {
        tech.domains.forEach(domain => {
          if (domains.includes(domain)) {
            data[tech.institutionId][domain]++;
          }
        });
      }
    });

    return data;
  }, [institutions, technologies, domains]);

  const maxValue = Math.max(
    ...Object.values(heatmapData).flatMap(inst => Object.values(inst))
  );

  const getHeatColor = (value: number) => {
    if (value === 0) return 'bg-muted';
    const intensity = value / maxValue;
    if (intensity > 0.7) return 'bg-accent';
    if (intensity > 0.4) return 'bg-accent/60';
    if (intensity > 0.2) return 'bg-accent/30';
    return 'bg-accent/10';
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">Institution Coverage</h3>
        <span className="text-xs font-mono text-muted-foreground">{institutions.length} institutions</span>
      </div>
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <div className="flex">
            <div className="w-24 flex-shrink-0" />
            <div className="flex gap-1">
              {domains.map(domain => (
                <div key={domain} className="w-12 text-center">
                  <span className="text-[10px] font-mono font-semibold text-muted-foreground uppercase">
                    {domainLabels[domain]}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-1 mt-2">
            {institutions.map((inst, index) => (
              <motion.div
                key={inst.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.03 }}
                className="flex items-center"
              >
                <div className="w-24 flex-shrink-0 pr-2">
                  <span className="text-xs font-medium text-foreground truncate block">
                    {inst.acronym}
                  </span>
                </div>
                <div className="flex gap-1">
                  {domains.map(domain => {
                    const value = heatmapData[inst.id]?.[domain] || 0;
                    return (
                      <motion.div
                        key={domain}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: index * 0.03 + 0.1 }}
                        className={`w-12 h-8 ${getHeatColor(value)} rounded-sm flex items-center justify-center group relative cursor-pointer hover:ring-2 hover:ring-accent transition-all`}
                      >
                        {value > 0 && (
                          <span className="text-[10px] font-mono font-semibold text-foreground">
                            {value}
                          </span>
                        )}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-popover border border-border rounded text-xs font-mono whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                          {inst.acronym}: {value} {domainLabels[domain]}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}