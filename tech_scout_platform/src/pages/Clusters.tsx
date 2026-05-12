import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, TrendingUp, Users, Award, ChevronRight, X } from 'lucide-react';
import { CLUSTERS, TECHNOLOGIES, INSTITUTIONS } from '@/data/index';
import { Cluster, Technology, TechDomain, LicensingStatus } from '@/lib/index';
import { EvidenceCard, InstitutionBadge } from '@/components/EvidenceCards';
import { ClusterForceGraph } from '@/components/Charts';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Separator } from '@/components/ui/separator';

export default function Clusters() {
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [domainFilter, setDomainFilter] = useState<string>('all');
  const [minClusterSize, setMinClusterSize] = useState<number>(0);
  const [institutionFilter, setInstitutionFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredClusters = useMemo(() => {
    return CLUSTERS.filter(cluster => {
      if (domainFilter !== 'all' && cluster.domain !== domainFilter) return false;
      if (cluster.size < minClusterSize) return false;
      if (institutionFilter !== 'all' && !cluster.institutionIds.includes(institutionFilter)) return false;
      if (searchQuery && !cluster.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [domainFilter, minClusterSize, institutionFilter, searchQuery]);

  const emergingClusters = useMemo(() => {
    return CLUSTERS.filter(c => c.size >= 5 && c.size <= 7).slice(0, 3);
  }, []);

  const handleClusterClick = (cluster: Cluster) => {
    if (compareMode) {
      if (selectedForCompare.includes(cluster.id)) {
        setSelectedForCompare(selectedForCompare.filter(id => id !== cluster.id));
      } else if (selectedForCompare.length < 2) {
        setSelectedForCompare([...selectedForCompare, cluster.id]);
      }
    } else {
      setSelectedCluster(cluster);
    }
  };

  const getClusterTechnologies = (cluster: Cluster): Technology[] => {
    return TECHNOLOGIES.filter(t => cluster.allTechnologyIds.includes(t.id));
  };

  const getLicensingStatusColor = (status: LicensingStatus) => {
    switch (status) {
      case LicensingStatus.AVAILABLE:
        return 'bg-chart-4/20 text-chart-4';
      case LicensingStatus.LICENSED:
        return 'bg-muted text-muted-foreground';
      case LicensingStatus.PENDING:
        return 'bg-accent/20 text-accent';
      default:
        return 'bg-secondary text-secondary-foreground';
    }
  };

  const ComparisonView = () => {
    if (selectedForCompare.length !== 2) return null;
    const cluster1 = CLUSTERS.find(c => c.id === selectedForCompare[0])!;
    const cluster2 = CLUSTERS.find(c => c.id === selectedForCompare[1])!;
    const tech1 = getClusterTechnologies(cluster1);
    const tech2 = getClusterTechnologies(cluster2);

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm overflow-auto p-8"
      >
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold tracking-tight">CLUSTER COMPARISON</h2>
            <Button variant="ghost" size="icon" onClick={() => { setCompareMode(false); setSelectedForCompare([]); }}>
              <X className="h-5 w-5" />
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-8">
            <div className="space-y-6">
              <Card className="p-6 border-2 border-primary">
                <h3 className="text-xl font-bold mb-4">{cluster1.name}</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Size</span>
                    <span className="font-mono font-semibold">{cluster1.size} technologies</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Avg Confidence</span>
                    <span className="font-mono font-semibold">{cluster1.averageConfidence}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Institutions</span>
                    <span className="font-mono font-semibold">{cluster1.institutionIds.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Licensing</span>
                    <Badge className={getLicensingStatusColor(cluster1.dominantLicensingStatus)}>
                      {cluster1.dominantLicensingStatus}
                    </Badge>
                  </div>
                </div>
                <Separator className="my-4" />
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Key Tags</p>
                  <div className="flex flex-wrap gap-2">
                    {cluster1.keyTags.map(tag => (
                      <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                    ))}
                  </div>
                </div>
              </Card>
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Technologies ({tech1.length})</h4>
                {tech1.slice(0, 5).map(tech => (
                  <Card key={tech.id} className="p-4">
                    <p className="font-semibold text-sm mb-1">{tech.title}</p>
                    <p className="text-xs text-muted-foreground">{tech.institutionAcronym} • {tech.patentNumber}</p>
                  </Card>
                ))}
              </div>
            </div>
            <div className="space-y-6">
              <Card className="p-6 border-2 border-accent">
                <h3 className="text-xl font-bold mb-4">{cluster2.name}</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Size</span>
                    <span className="font-mono font-semibold">{cluster2.size} technologies</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Avg Confidence</span>
                    <span className="font-mono font-semibold">{cluster2.averageConfidence}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Institutions</span>
                    <span className="font-mono font-semibold">{cluster2.institutionIds.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Licensing</span>
                    <Badge className={getLicensingStatusColor(cluster2.dominantLicensingStatus)}>
                      {cluster2.dominantLicensingStatus}
                    </Badge>
                  </div>
                </div>
                <Separator className="my-4" />
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Key Tags</p>
                  <div className="flex flex-wrap gap-2">
                    {cluster2.keyTags.map(tag => (
                      <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                    ))}
                  </div>
                </div>
              </Card>
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Technologies ({tech2.length})</h4>
                {tech2.slice(0, 5).map(tech => (
                  <Card key={tech.id} className="p-4">
                    <p className="font-semibold text-sm mb-1">{tech.title}</p>
                    <p className="text-xs text-muted-foreground">{tech.institutionAcronym} • {tech.patentNumber}</p>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  const ClusterDetailView = () => {
    if (!selectedCluster) return null;
    const technologies = getClusterTechnologies(selectedCluster);

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-background overflow-auto"
      >
        <div className="min-h-screen p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-4xl font-bold tracking-tight mb-2">{selectedCluster.name}</h2>
                <div className="flex items-center gap-4 text-muted-foreground">
                  <span className="font-mono">{selectedCluster.size} technologies</span>
                  <span>•</span>
                  <span className="font-mono">{selectedCluster.averageConfidence}% avg confidence</span>
                  <span>•</span>
                  <span>{selectedCluster.institutionIds.length} institutions</span>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setSelectedCluster(null)}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="mb-8">
              <Card className="p-6">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-4">Cluster Visualization</h3>
                <ClusterForceGraph technologies={technologies} clusterName={selectedCluster.name} />
              </Card>
            </div>

            <div className="space-y-4">
              <h3 className="text-2xl font-bold tracking-tight">All Technologies in Cluster</h3>
              {technologies.map(tech => (
                <EvidenceCard key={tech.id} technology={tech} />
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold tracking-tight mb-2">OPPORTUNITY CLUSTERS</h1>
              <p className="text-muted-foreground">AI-GENERATED TECHNOLOGY GROUPINGS</p>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant={compareMode ? 'default' : 'outline'}
                onClick={() => {
                  setCompareMode(!compareMode);
                  setSelectedForCompare([]);
                }}
              >
                {compareMode ? 'Exit Compare Mode' : 'Compare Clusters'}
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search clusters..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={domainFilter} onValueChange={setDomainFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Domain" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Domains</SelectItem>
                {Object.values(TechDomain).map(domain => (
                  <SelectItem key={domain} value={domain}>{domain}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={institutionFilter} onValueChange={setInstitutionFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Institution" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Institutions</SelectItem>
                {INSTITUTIONS.map(inst => (
                  <SelectItem key={inst.id} value={inst.id}>{inst.acronym}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex items-center gap-3">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1">
                <Slider
                  value={[minClusterSize]}
                  onValueChange={(v) => setMinClusterSize(v[0])}
                  max={10}
                  step={1}
                  className="w-full"
                />
              </div>
              <span className="text-xs text-muted-foreground font-mono w-8">{minClusterSize}+</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-8">
        {compareMode && selectedForCompare.length > 0 && (
          <div className="mb-6 p-4 bg-accent/10 border border-accent rounded-lg">
            <p className="text-sm font-semibold mb-2">Selected for comparison: {selectedForCompare.length}/2</p>
            <div className="flex gap-2">
              {selectedForCompare.map(id => {
                const cluster = CLUSTERS.find(c => c.id === id)!;
                return (
                  <Badge key={id} variant="secondary" className="gap-2">
                    {cluster.name}
                    <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedForCompare(selectedForCompare.filter(cid => cid !== id))} />
                  </Badge>
                );
              })}
            </div>
          </div>
        )}

        <div className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="h-5 w-5 text-accent" />
            <h2 className="text-2xl font-bold tracking-tight">EMERGING CLUSTERS</h2>
            <Badge variant="secondary" className="ml-auto">Newly Identified</Badge>
          </div>
          <div className="grid grid-cols-3 gap-6">
            {emergingClusters.map(cluster => (
              <motion.div
                key={cluster.id}
                whileHover={{ scale: 1.02 }}
                className="cursor-pointer"
                onClick={() => handleClusterClick(cluster)}
              >
                <Card className="p-6 border-2 border-accent/50 hover:border-accent transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-bold">{cluster.name}</h3>
                    <Badge className="bg-accent/20 text-accent">NEW</Badge>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Size</span>
                      <span className="font-mono font-semibold">{cluster.size}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Confidence</span>
                      <span className="font-mono font-semibold">{cluster.averageConfidence}%</span>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-6">ALL CLUSTERS ({filteredClusters.length})</h2>
          <div className="grid grid-cols-2 gap-6">
            {filteredClusters.map(cluster => {
              const isSelected = compareMode && selectedForCompare.includes(cluster.id);
              return (
                <motion.div
                  key={cluster.id}
                  whileHover={{ scale: 1.01 }}
                  className="cursor-pointer"
                  onClick={() => handleClusterClick(cluster)}
                >
                  <Card className={`p-6 transition-all ${
                    isSelected ? 'border-2 border-primary bg-primary/5' : 'hover:border-primary/50'
                  }`}>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold mb-2">{cluster.name}</h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Users className="h-4 w-4" />
                          <span className="font-mono">{cluster.size} technologies</span>
                          <span>•</span>
                          <Award className="h-4 w-4" />
                          <span className="font-mono">{cluster.averageConfidence}% confidence</span>
                        </div>
                      </div>
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    </div>

                    <div className="mb-4">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Institutions</p>
                      <div className="flex flex-wrap gap-2">
                        {cluster.institutionIds.slice(0, 5).map(instId => {
                          const inst = INSTITUTIONS.find(i => i.id === instId);
                          if (!inst) return null;
                          return (
                            <InstitutionBadge key={instId} acronym={inst.acronym} fullName={inst.name} />
                          );
                        })}
                        {cluster.institutionIds.length > 5 && (
                          <Badge variant="secondary" className="text-xs">+{cluster.institutionIds.length - 5}</Badge>
                        )}
                      </div>
                    </div>

                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Licensing Status</p>
                        <Badge className={getLicensingStatusColor(cluster.dominantLicensingStatus)}>
                          {cluster.dominantLicensingStatus}
                        </Badge>
                      </div>
                    </div>

                    <div className="mb-4">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Key Tags</p>
                      <div className="flex flex-wrap gap-2">
                        {cluster.keyTags.map(tag => (
                          <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                        ))}
                      </div>
                    </div>

                    <Separator className="my-4" />

                    <div>
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Top Technologies</p>
                      <div className="space-y-2">
                        {cluster.topTechnologies.slice(0, 3).map(tech => (
                          <div key={tech.id} className="flex items-start gap-3 p-2 rounded bg-muted/30">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-semibold truncate">{tech.title}</p>
                              <p className="text-xs text-muted-foreground">
                                {tech.institutionAcronym} • {tech.patentNumber}
                              </p>
                            </div>
                            <span className="text-xs font-mono font-semibold text-accent">{tech.confidenceScore}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {selectedCluster && <ClusterDetailView />}
        {compareMode && selectedForCompare.length === 2 && <ComparisonView />}
      </AnimatePresence>
    </div>
  );
}
