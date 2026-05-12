import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ExternalLink, ChevronDown, ChevronUp, Table as TableIcon, Grid3x3 } from 'lucide-react';
import { INSTITUTIONS, TECHNOLOGIES } from '@/data/index';
import { Institution, Technology, CoverageStatus, LicensingStatus, TechDomain } from '@/lib/index';
import { EvidenceCard, InstitutionBadge } from '@/components/EvidenceCards';
import { DomainDistributionChart } from '@/components/Charts';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const ITEMS_PER_PAGE = 10;

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

const getLicensingStatusColor = (status: LicensingStatus) => {
  switch (status) {
    case LicensingStatus.AVAILABLE:
      return 'bg-chart-1 text-chart-1-foreground';
    case LicensingStatus.LICENSED:
      return 'bg-muted text-muted-foreground';
    case LicensingStatus.PENDING:
      return 'bg-accent text-accent-foreground';
    case LicensingStatus.NOT_AVAILABLE:
      return 'bg-destructive text-destructive-foreground';
    case LicensingStatus.CONTACT_TTO:
      return 'bg-secondary text-secondary-foreground';
    default:
      return 'bg-muted text-muted-foreground';
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
};

export default function Catalogs() {
  const [selectedInstitution, setSelectedInstitution] = useState<Institution | null>(INSTITUTIONS[0]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'techCount' | 'lastCrawled'>('name');
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const filteredInstitutions = useMemo(() => {
    let filtered = INSTITUTIONS;

    if (searchQuery) {
      filtered = filtered.filter(inst =>
        inst.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inst.acronym.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(inst => inst.coverageStatus === statusFilter);
    }

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'techCount':
          return b.techCount - a.techCount;
        case 'lastCrawled':
          return new Date(b.lastCrawled || 0).getTime() - new Date(a.lastCrawled || 0).getTime();
        default:
          return 0;
      }
    });
  }, [searchQuery, statusFilter, sortBy]);

  const institutionTechnologies = useMemo(() => {
    if (!selectedInstitution) return [];
    return TECHNOLOGIES.filter(tech => tech.institutionId === selectedInstitution.id)
      .sort((a, b) => new Date(b.filingDate).getTime() - new Date(a.filingDate).getTime());
  }, [selectedInstitution]);

  const paginatedTechnologies = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return institutionTechnologies.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [institutionTechnologies, currentPage]);

  const totalPages = Math.ceil(institutionTechnologies.length / ITEMS_PER_PAGE);

  const recentAdditions = useMemo(() => {
    return institutionTechnologies.slice(0, 4);
  }, [institutionTechnologies]);

  return (
    <div className="flex h-full">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="w-80 border-r border-border bg-card p-6 overflow-y-auto"
      >
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold mb-4">INSTITUTIONS</h2>
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search institutions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 font-mono text-sm"
              />
            </div>
            <div className="space-y-2 mb-4">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full">
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
              <Select value={sortBy} onValueChange={(v) => setSortBy(v as any)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="techCount">Tech Count</SelectItem>
                  <SelectItem value="lastCrawled">Last Crawled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            {filteredInstitutions.map((inst) => (
              <motion.button
                key={inst.id}
                onClick={() => {
                  setSelectedInstitution(inst);
                  setCurrentPage(1);
                }}
                className={`w-full text-left p-3 rounded-lg border transition-all ${
                  selectedInstitution?.id === inst.id
                    ? 'bg-primary/10 border-primary'
                    : 'bg-card border-border hover:bg-muted'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${getCoverageStatusColor(inst.coverageStatus)}`} />
                    <span className="font-semibold text-sm">{inst.acronym}</span>
                  </div>
                  <span className="font-mono text-xs text-muted-foreground">{inst.techCount}</span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-1">{inst.name}</p>
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        className="flex-1 overflow-y-auto p-8"
      >
        {selectedInstitution ? (
          <div className="space-y-8">
            <div>
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">{selectedInstitution.name}</h1>
                  <p className="text-muted-foreground">{selectedInstitution.ttoOfficeName}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getCoverageStatusColor(selectedInstitution.coverageStatus)}`} />
                  <span className="text-sm font-medium uppercase">{selectedInstitution.coverageStatus}</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-6">
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground mb-1">Total Inventions</p>
                  <p className="text-3xl font-bold font-mono">{selectedInstitution.techCount}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground mb-1">Last Crawled</p>
                  <p className="text-lg font-mono">{formatDate(selectedInstitution.lastCrawled)}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground mb-1">Catalog URL</p>
                  <a
                    href={selectedInstitution.catalogUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1 font-mono"
                  >
                    View Catalog <ExternalLink className="h-3 w-3" />
                  </a>
                </Card>
              </div>

              {selectedInstitution.missionStatement && (
                <Card className="p-4 mb-6">
                  <p className="text-sm text-muted-foreground mb-2">Mission Statement</p>
                  <p className="text-sm">{selectedInstitution.missionStatement}</p>
                </Card>
              )}

              {selectedInstitution.licensingContact && (
                <Card className="p-4 mb-6">
                  <p className="text-sm text-muted-foreground mb-2">Licensing Contact</p>
                  <p className="text-sm font-mono">{selectedInstitution.licensingContact}</p>
                </Card>
              )}
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">TECHNOLOGY DOMAIN DISTRIBUTION</h2>
              <Card className="p-6">
                <DomainDistributionChart technologies={institutionTechnologies} />
              </Card>
            </div>

            {recentAdditions.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold mb-4">RECENT ADDITIONS</h2>
                <div className="grid grid-cols-2 gap-4">
                  {recentAdditions.map((tech) => (
                    <Card key={tech.id} className="p-4 hover:shadow-lg transition-shadow">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold text-sm line-clamp-2 flex-1">{tech.title}</h3>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className={getLicensingStatusColor(tech.licensingStatus)} variant="secondary">
                          {tech.licensingStatus.replace('_', ' ')}
                        </Badge>
                        <span className="font-mono text-xs text-muted-foreground">{tech.patentNumber}</span>
                      </div>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {tech.domains.slice(0, 3).map((domain) => (
                          <Badge key={domain} variant="outline" className="text-xs">
                            {domain.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Filed: {formatDate(tech.filingDate)}</span>
                        <span className="font-mono">Confidence: {tech.confidenceScore}%</span>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">ALL TECHNOLOGIES ({institutionTechnologies.length})</h2>
                <div className="flex items-center gap-2">
                  <Button
                    variant={viewMode === 'cards' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('cards')}
                  >
                    <Grid3x3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'table' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('table')}
                  >
                    <TableIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {viewMode === 'cards' ? (
                <div className="space-y-4">
                  {paginatedTechnologies.map((tech) => (
                    <EvidenceCard key={tech.id} technology={tech} />
                  ))}
                </div>
              ) : (
                <Card>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Title</TableHead>
                        <TableHead>Patent #</TableHead>
                        <TableHead>Domain</TableHead>
                        <TableHead>Filing Date</TableHead>
                        <TableHead>Licensing Status</TableHead>
                        <TableHead>Confidence</TableHead>
                        <TableHead>Source</TableHead>
                        <TableHead></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {paginatedTechnologies.map((tech) => (
                        <>
                          <TableRow
                            key={tech.id}
                            className="cursor-pointer hover:bg-muted/50"
                            onClick={() => setExpandedRow(expandedRow === tech.id ? null : tech.id)}
                          >
                            <TableCell className="font-medium max-w-xs">
                              <div className="line-clamp-2">{tech.title}</div>
                            </TableCell>
                            <TableCell className="font-mono text-sm">{tech.patentNumber}</TableCell>
                            <TableCell>
                              <Badge variant="outline" className="text-xs">
                                {tech.domains[0]?.replace('_', ' ')}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-sm">{formatDate(tech.filingDate)}</TableCell>
                            <TableCell>
                              <Badge className={getLicensingStatusColor(tech.licensingStatus)} variant="secondary">
                                {tech.licensingStatus.replace('_', ' ')}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-sm">{tech.confidenceScore}%</TableCell>
                            <TableCell>
                              <a
                                href={tech.sourceUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary hover:underline flex items-center gap-1"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <ExternalLink className="h-3 w-3" />
                              </a>
                            </TableCell>
                            <TableCell>
                              {expandedRow === tech.id ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                            </TableCell>
                          </TableRow>
                          <AnimatePresence>
                            {expandedRow === tech.id && (
                              <TableRow>
                                <TableCell colSpan={8} className="bg-muted/30">
                                  <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="p-4 space-y-3"
                                  >
                                    <div>
                                      <p className="text-sm font-semibold mb-1">Abstract</p>
                                      <p className="text-sm text-muted-foreground">{tech.abstract}</p>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                      <div>
                                        <p className="text-xs text-muted-foreground mb-1">All Domains</p>
                                        <div className="flex flex-wrap gap-1">
                                          {tech.domains.map((domain) => (
                                            <Badge key={domain} variant="outline" className="text-xs">
                                              {domain.replace('_', ' ')}
                                            </Badge>
                                          ))}
                                        </div>
                                      </div>
                                      <div>
                                        <p className="text-xs text-muted-foreground mb-1">Inventors</p>
                                        <p className="text-sm">{tech.inventors.join(', ')}</p>
                                      </div>
                                    </div>
                                  </motion.div>
                                </TableCell>
                              </TableRow>
                            )}
                          </AnimatePresence>
                        </>
                      ))}
                    </TableBody>
                  </Table>
                </Card>
              )}

              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-6">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  <span className="text-sm font-mono">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">Select an institution to view catalog details</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
