import axios from 'axios';

function resolveRagApiBaseUrl() {
  const configuredBaseUrl = import.meta.env.VITE_RAG_API_BASE_URL?.trim();

  if (configuredBaseUrl) {
    return configuredBaseUrl.replace(/\/$/, '');
  }

  if (typeof window !== 'undefined') {
    const { hostname } = window.location;

    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
  }

  return '';
}

const ragApi = axios.create({
  baseURL: resolveRagApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface RagSearchFilters {
  organization_names?: string[];
  organization_types?: string[];
  categories?: string[];
  direct_source_only?: boolean;
  licensing_statuses?: string[];
}

export interface RagSearchRequest {
  query: string;
  filters?: RagSearchFilters;
  top_k?: number;
  include_answer?: boolean;
}

export interface RagEvidenceChunk {
  chunk_id: string;
  text: string;
  source_url: string;
}

export interface RagTechnologyResult {
  technology_id: string;
  title: string;
  organization_name: string;
  organization_type: string;
  source_url: string;
  catalog_family: string;
  licensing_status: string;
  score: number;
  summary: string;
  tags: string[];
  published_at: string | null;
  evidence: RagEvidenceChunk[];
}

export interface RagAnswer {
  summary: string;
  model: string;
  generated_at: string;
}

export interface RagCoverageStatus {
  direct_covered_count: number;
  target_count: number;
  snapshot_record_count: number;
  covered_family_count: number;
  family_target_count: number;
}

export interface RagSearchResponse {
  query: string;
  answer: RagAnswer | null;
  results: RagTechnologyResult[];
  coverage: RagCoverageStatus;
}

export interface RagTechnologyDetail {
  technology_id: string;
  title: string;
  organization_name: string;
  organization_type: string;
  source_url: string;
  catalog_family: string;
  licensing_status: string;
  summary: string;
  full_text: string;
  tags: string[];
  published_at: string | null;
  evidence: RagEvidenceChunk[];
}

export async function searchRagTechnologies(payload: RagSearchRequest): Promise<RagSearchResponse> {
  const response = await ragApi.post<RagSearchResponse>('/rag/search', payload);
  return response.data;
}

export async function getRagCoverage(): Promise<RagCoverageStatus> {
  const response = await ragApi.get<RagCoverageStatus>('/rag/coverage');
  return response.data;
}

export async function getRagTechnologyDetail(technologyId: string): Promise<RagTechnologyDetail> {
  const response = await ragApi.get<RagTechnologyDetail>(`/rag/technologies/${technologyId}`);
  return response.data;
}