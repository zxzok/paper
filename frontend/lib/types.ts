export type Template = {
  identifier: string;
  display_name: string;
  license: string;
  description?: string;
  engine: string;
  citation_package: string;
  assets_path: string;
};

export type ProjectCreateResponse = {
  id: string;
  status: string;
  created_at: string;
};

export type CitationSlot = {
  sentence: string;
  need_citation: boolean;
  reasons: string[];
  query_terms: string[];
  confidence: number;
  status: string;
};

export type Reference = {
  key: string;
  title: string;
  authors: string[];
  venue?: string | null;
  year?: number | null;
  doi?: string | null;
  url?: string | null;
  source?: string | null;
  score?: number | null;
  needs_review?: boolean;
};

export type PreflightIssue = {
  code: string;
  severity: string;
  message: string;
};

export type PreflightReport = {
  project_id: string;
  generated_at: string;
  issues: PreflightIssue[];
  summary: Record<string, string | number>;
};
