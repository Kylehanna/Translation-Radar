import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Download, SlidersHorizontal, Sparkles } from 'lucide-react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { EvidenceCard, EvidenceCardSkeleton } from '@/components/EvidenceCards';
import { AgentStatusBadge } from '@/components/AgentStatusPanel';
import { SEARCH_EXAMPLES } from '@/data/index';
import { AgentStatus, LicensingStatus, ProvenanceLevel, TechDomain, Technology, SearchMessage } from '@/lib/index';
import { RagSearchResponse, RagTechnologyResult, searchRagTechnologies } from '@/api/rag';

const AGENT_OPTIONS = [
  { id: 'agent-crawler-01', name: 'CRAWLER-01', type: 'Primary Crawler' },
  { id: 'agent-validator-01', name: 'VALIDATOR-01', type: 'Source Validator' },
  { id: 'agent-summarizer-01', name: 'SUMMARIZER-01', type: 'Content Summarizer' },
  { id: 'agent-ranker-01', name: 'RANKER-01', type: 'Confidence Ranker' },
];

const SORT_OPTIONS = [
  { value: 'confidence', label: 'Confidence Score' },
  { value: 'institution', label: 'Institution' },
  { value: 'date', label: 'Filing Date' },
  { value: 'relevance', label: 'Relevance' },
];

interface SearchResultView {
  technology: Technology;
  raw: RagTechnologyResult;
}

const ORGANIZATION_ACRONYMS: Record<string, string> = {
  'University of Southern California': 'USC',
  'H. Lee Moffitt Cancer Center & Research Institute': 'MOFFITT',
  'University of Texas at El Paso': 'UTEP',
  'Stanford University': 'STANFORD',
  'Icahn School of Medicine at Mount Sinai': 'MOUNT SINAI',
};

function deriveInstitutionAcronym(organizationName: string) {
  if (ORGANIZATION_ACRONYMS[organizationName]) {
    return ORGANIZATION_ACRONYMS[organizationName];
  }

  const parts = organizationName
    .replace(/&/g, ' ')
    .split(/\s+/)
    .filter((part) => part.length > 0 && !['of', 'and', 'the', 'at'].includes(part.toLowerCase()));

  if (parts.length === 0) {
    return organizationName.slice(0, 8).toUpperCase();
  }

  if (parts.length === 1) {
    return parts[0].slice(0, 8).toUpperCase();
  }

  return parts.slice(0, 4).map((part) => part[0]).join('').toUpperCase();
}

function mapLicensingStatus(status: string): LicensingStatus {
  switch (status.toLowerCase()) {
    case 'available':
      return LicensingStatus.AVAILABLE;
    case 'licensed':
      return LicensingStatus.LICENSED;
    case 'pending':
      return LicensingStatus.PENDING;
    case 'contact-tto':
    case 'contact_tto':
      return LicensingStatus.CONTACT_TTO;
    default:
      return LicensingStatus.AVAILABLE;
  }
}

function mapTagToDomain(tag: string): TechDomain {
  const value = tag.toLowerCase();

  if (value.includes('oncology') || value.includes('cancer')) return TechDomain.ONCOLOGY;
  if (value.includes('ai') || value.includes('software')) return TechDomain.AI_ML;
  if (value.includes('imaging')) return TechDomain.MEDICAL_IMAGING;
  if (value.includes('diagnostic') || value.includes('biomarker')) return TechDomain.DIAGNOSTICS;
  if (value.includes('therapeutic')) return TechDomain.THERAPEUTICS;
  if (value.includes('sensor') || value.includes('hardware')) return TechDomain.DEVICES;
  if (value.includes('quantum') || value.includes('material') || value.includes('memristor')) return TechDomain.MATERIALS;

  return TechDomain.BIOTECH;
}

function mapOrganizationTypeToDomain(organizationType: string): TechDomain {
  switch (organizationType.toLowerCase()) {
    case 'cancer_center':
      return TechDomain.ONCOLOGY;
    case 'medical_school':
      return TechDomain.DIAGNOSTICS;
    default:
      return TechDomain.BIOTECH;
  }
}

function normalizeConfidenceScore(score: number, maxScore: number) {
  if (maxScore <= 0) return 60;
  return Math.max(55, Math.min(99, Math.round((score / maxScore) * 100)));
}

function buildConfidenceDistribution(results: SearchResultView[]) {
  return [
    { range: '90-100', count: results.filter(({ technology }) => technology.confidenceScore >= 90).length },
    { range: '80-89', count: results.filter(({ technology }) => technology.confidenceScore >= 80 && technology.confidenceScore < 90).length },
    { range: '70-79', count: results.filter(({ technology }) => technology.confidenceScore >= 70 && technology.confidenceScore < 80).length },
    { range: '<70', count: results.filter(({ technology }) => technology.confidenceScore < 70).length },
  ];
}

function mapRagResultToTechnology(result: RagTechnologyResult, maxScore: number): Technology {
  const domains = Array.from(new Set(result.tags.map(mapTagToDomain)));
  const institutionAcronym = deriveInstitutionAcronym(result.organization_name);

  return {
    id: result.technology_id,
    title: result.title,
    institutionId: result.organization_name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
    institutionName: result.organization_name,
    institutionAcronym,
    patentNumber: result.technology_id,
    abstract: result.summary,
    licensingStatus: mapLicensingStatus(result.licensing_status),
    domains: domains.length > 0 ? domains : [mapOrganizationTypeToDomain(result.organization_type)],
    confidenceScore: normalizeConfidenceScore(result.score, maxScore),
    provenanceLevel: ProvenanceLevel.DIRECT_SOURCE_VERIFIED,
    sourceUrl: result.source_url,
    agentValidated: true,
    filingDate: result.published_at ?? 'N/A',
    inventors: result.tags,
    agentId: result.catalog_family,
  };
}

function resolveSearchMessage(response: RagSearchResponse, mappedResults: SearchResultView[]) {
  if (response.answer?.summary) {
    return response.answer.summary;
  }

  if (mappedResults.length === 0) {
    return `No technologies matched '${response.query}'.`;
  }

  return `Found ${mappedResults.length} technologies with direct-source evidence across ${response.coverage.direct_covered_count} covered institutions.`;
}

function resolveApiError(error: unknown) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (error.message) {
      return error.message;
    }
  }

  return 'Search failed. Check VITE_RAG_API_BASE_URL and backend availability.';
}

export default function Search() {
  const [prompt, setPrompt] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('agent-crawler-01');
  const [messages, setMessages] = useState<SearchMessage[]>([]);
  const [results, setResults] = useState<SearchResultView[]>([]);
  const [selectedTech, setSelectedTech] = useState<SearchResultView | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [sortBy, setSortBy] = useState('confidence');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % SEARCH_EXAMPLES.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const extractEntities = (query: string) => {
    const institutions: string[] = [];
    const domains: string[] = [];
    const filters: string[] = [];

    const institutionKeywords = ['MIT', 'Stanford', 'USC', 'Moffitt', 'Johns Hopkins', 'JHU', 'Caltech', 'Harvard'];
    const domainKeywords = ['oncology', 'AI', 'ML', 'imaging', 'biotech', 'cleantech', 'medtech', 'diagnostics', 'therapeutics'];
    const filterKeywords = ['licensing available', 'licensed', 'high confidence', 'FDA approval'];

    institutionKeywords.forEach(inst => {
      if (query.toLowerCase().includes(inst.toLowerCase())) {
        institutions.push(inst);
      }
    });

    domainKeywords.forEach(domain => {
      if (query.toLowerCase().includes(domain.toLowerCase())) {
        domains.push(domain);
      }
    });

    filterKeywords.forEach(filter => {
      if (query.toLowerCase().includes(filter.toLowerCase())) {
        filters.push(filter);
      }
    });

    return { institutions, domains, filters };
  };

  const handleSearch = async () => {
    if (!prompt.trim()) return;

    const userMessage: SearchMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: prompt,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setPrompt('');
    setIsSearching(true);
    setIsTyping(true);

    const startedAt = performance.now();

    try {
      const response = await searchRagTechnologies({
        query: userMessage.content,
        top_k: 12,
        include_answer: true,
      });

      const maxScore = response.results.reduce((highest, result) => Math.max(highest, result.score), 0);
      const mappedResults = response.results.map((result) => ({
        technology: mapRagResultToTechnology(result, maxScore),
        raw: result,
      }));

      const systemMessage: SearchMessage = {
        id: `msg-${Date.now() + 1}`,
        type: 'system',
        content: resolveSearchMessage(response, mappedResults),
        timestamp: new Date().toISOString(),
        agentId: selectedAgent,
        resultCount: mappedResults.length,
        processingTime: Number(((performance.now() - startedAt) / 1000).toFixed(2)),
        confidenceDistribution: buildConfidenceDistribution(mappedResults),
      };

      setMessages(prev => [...prev, systemMessage]);
      setResults(mappedResults);
      setSelectedTech(prev => prev && mappedResults.some((result) => result.technology.id === prev.technology.id) ? prev : null);
    } catch (error) {
      const systemMessage: SearchMessage = {
        id: `msg-${Date.now() + 1}`,
        type: 'system',
        content: resolveApiError(error),
        timestamp: new Date().toISOString(),
        agentId: selectedAgent,
        resultCount: 0,
        processingTime: Number(((performance.now() - startedAt) / 1000).toFixed(2)),
      };

      setMessages(prev => [...prev, systemMessage]);
      setResults([]);
      setSelectedTech(null);
    } finally {
      setIsTyping(false);
      setIsSearching(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setPrompt(example);
    textareaRef.current?.focus();
  };

  const sortedResults = [...results].sort((a, b) => {
    switch (sortBy) {
      case 'confidence':
        return b.technology.confidenceScore - a.technology.confidenceScore;
      case 'institution':
        return a.technology.institutionName.localeCompare(b.technology.institutionName);
      case 'date':
        return new Date(b.raw.published_at ?? 0).getTime() - new Date(a.raw.published_at ?? 0).getTime();
      case 'relevance':
        return b.raw.score - a.raw.score;
      default:
        return 0;
    }
  });

  const entities = prompt ? extractEntities(prompt) : null;

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden p-6">
          <div className="flex-1 overflow-y-auto space-y-6 mb-6" ref={resultsRef}>
            {messages.length === 0 && results.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center h-full space-y-8"
              >
                <div className="text-center space-y-4 max-w-2xl">
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 text-accent text-sm font-mono">
                    <Sparkles className="w-4 h-4" />
                    SCOUT COMMAND — AI-POWERED TECHNOLOGY INTELLIGENCE
                  </div>
                  <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Search University TTO Catalogs
                  </h1>
                  <p className="text-lg text-muted-foreground">
                    Ask our AI agents to find licensable technologies, compare inventions, and trace provenance across institutions.
                  </p>
                </div>

                <div className="w-full max-w-3xl">
                  <p className="text-sm font-mono text-muted-foreground mb-3 uppercase tracking-wide">Example Queries</p>
                  <div className="grid grid-cols-2 gap-3">
                    {SEARCH_EXAMPLES.slice(0, 6).map((example, idx) => (
                      <motion.button
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        onClick={() => handleExampleClick(example)}
                        className="text-left p-4 rounded-lg border border-border bg-card hover:bg-accent/5 hover:border-accent/50 transition-all text-sm text-card-foreground"
                      >
                        {example}
                      </motion.button>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {messages.length > 0 && (
              <div className="space-y-4 max-w-4xl mx-auto">
                {messages.map((message, idx) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.type === 'user' ? (
                      <div className="max-w-2xl bg-card border border-border rounded-lg px-6 py-4">
                        <p className="text-foreground">{message.content}</p>
                      </div>
                    ) : (
                      <div className="max-w-3xl space-y-3">
                        <div className="flex items-center gap-3">
                          <AgentStatusBadge status={AgentStatus.COMPLETED} size="sm" />
                          <span className="text-xs font-mono text-muted-foreground">{message.agentId}</span>
                          <span className="text-xs text-muted-foreground">•</span>
                          <span className="text-xs text-muted-foreground">{message.processingTime}s</span>
                        </div>
                        <div className="bg-sidebar/5 border border-sidebar/20 rounded-lg px-6 py-4">
                          <p className="text-sidebar-foreground">{message.content}</p>
                          {message.confidenceDistribution && (
                            <div className="mt-4 flex items-center gap-4 text-xs font-mono">
                              {message.confidenceDistribution.map((dist, i) => (
                                <div key={i} className="flex items-center gap-2">
                                  <span className="text-muted-foreground">{dist.range}:</span>
                                  <span className="text-accent font-semibold">{dist.count}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
                {isTyping && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start"
                  >
                    <div className="bg-sidebar/5 border border-sidebar/20 rounded-lg px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                        <div className="w-2 h-2 rounded-full bg-accent animate-pulse" style={{ animationDelay: '0.2s' }} />
                        <div className="w-2 h-2 rounded-full bg-accent animate-pulse" style={{ animationDelay: '0.4s' }} />
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )}

            {results.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <h2 className="text-2xl font-bold tracking-tight">
                      {results.length} Results
                    </h2>
                    <Separator orientation="vertical" className="h-6" />
                    <Select value={sortBy} onValueChange={setSortBy}>
                      <SelectTrigger className="w-48">
                        <SlidersHorizontal className="w-4 h-4 mr-2" />
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {SORT_OPTIONS.map(option => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export Results
                  </Button>
                </div>

                <div className="grid gap-4">
                  {isSearching ? (
                    Array.from({ length: 3 }).map((_, i) => (
                      <EvidenceCardSkeleton key={i} />
                    ))
                  ) : (
                    sortedResults.map((result, idx) => (
                      <motion.div
                        key={result.technology.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        onClick={() => setSelectedTech(result)}
                        className="cursor-pointer"
                      >
                        <EvidenceCard technology={result.technology} />
                      </motion.div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </div>

          <div className="space-y-4">
            {entities && (entities.institutions.length > 0 || entities.domains.length > 0 || entities.filters.length > 0) && (
              <Card className="p-4 bg-accent/5 border-accent/20">
                <div className="flex items-start gap-3">
                  <Sparkles className="w-4 h-4 text-accent mt-0.5" />
                  <div className="flex-1 space-y-2">
                    <p className="text-xs font-mono text-muted-foreground uppercase tracking-wide">Query Intelligence</p>
                    <div className="flex flex-wrap gap-2">
                      {entities.institutions.length > 0 && (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">Institutions:</span>
                          {entities.institutions.map((inst, i) => (
                            <Badge key={i} variant="outline" className="text-xs">{inst}</Badge>
                          ))}
                        </div>
                      )}
                      {entities.domains.length > 0 && (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">Domains:</span>
                          {entities.domains.map((domain, i) => (
                            <Badge key={i} variant="outline" className="text-xs">{domain}</Badge>
                          ))}
                        </div>
                      )}
                      {entities.filters.length > 0 && (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">Filters:</span>
                          {entities.filters.map((filter, i) => (
                            <Badge key={i} variant="outline" className="text-xs">{filter}</Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            )}

            <div className="flex gap-3">
              <Select value={selectedAgent} onValueChange={setSelectedAgent}>
                <SelectTrigger className="w-64">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {AGENT_OPTIONS.map(agent => (
                    <SelectItem key={agent.id} value={agent.id}>
                      <div className="flex flex-col items-start">
                        <span className="font-mono text-sm">{agent.name}</span>
                        <span className="text-xs text-muted-foreground">{agent.type}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <div className="flex-1 relative">
                <Textarea
                  ref={textareaRef}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSearch();
                    }
                  }}
                  placeholder={SEARCH_EXAMPLES[placeholderIndex]}
                  className="min-h-[80px] pr-12 font-mono text-sm resize-none bg-card border-border focus:border-accent"
                />
                <Button
                  onClick={handleSearch}
                  disabled={!prompt.trim() || isSearching}
                  size="icon"
                  className="absolute bottom-3 right-3 bg-accent hover:bg-accent/90"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {selectedTech && (
          <motion.div
            initial={{ x: 380, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 380, opacity: 0 }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="w-[380px] border-l border-border bg-card overflow-y-auto p-6"
          >
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <h3 className="text-lg font-bold tracking-tight">Technology Detail</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedTech(null)}
                >
                  ✕
                </Button>
              </div>
              <EvidenceCard technology={selectedTech.technology} />
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-mono text-muted-foreground uppercase tracking-wide mb-2">Summary</p>
                  <p className="text-sm text-foreground leading-relaxed">{selectedTech.raw.summary}</p>
                </div>
                <Separator />
                <div>
                  <p className="text-xs font-mono text-muted-foreground uppercase tracking-wide mb-2">Technology ID</p>
                  <p className="text-sm text-foreground font-mono">{selectedTech.raw.technology_id}</p>
                </div>
                <Separator />
                <div>
                  <p className="text-xs font-mono text-muted-foreground uppercase tracking-wide mb-2">Tags</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedTech.raw.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                <Separator />
                <div>
                  <p className="text-xs font-mono text-muted-foreground uppercase tracking-wide mb-2">Evidence</p>
                  <p className="text-sm text-foreground leading-relaxed">
                    {selectedTech.raw.evidence[0]?.text ?? 'No evidence excerpt available.'}
                  </p>
                </div>
                <Separator />
                <div>
                  <p className="text-xs font-mono text-muted-foreground uppercase tracking-wide mb-2">Source Verification</p>
                  <a
                    href={selectedTech.raw.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-accent hover:underline font-mono break-all"
                  >
                    {selectedTech.raw.source_url}
                  </a>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
