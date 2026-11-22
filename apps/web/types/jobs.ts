export type JobSkill = {
  id: string;
  skill_name: string;
  skill_type: string | null;
};

export type JobListItem = {
  id: string;
  title: string;
  company_name: string;
  location: string | null;
  workplace_type: string | null;
  employment_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  posted_at: string | null;
  is_active: boolean;
  source_url: string | null;
  experience_level: string | null;
  created_at: string;
  updated_at: string;
  match_score?: number | null;
  recommendation?: string | null;
};

export type Job = JobListItem & {
  company_url: string | null;
  description: string | null;
  locations: string[];
  department: string | null;
  expires_at: string | null;
  external_id: string | null;
  source_id: string | null;
  source_type: string | null;
  source_name: string | null;
  skills: JobSkill[];
};

export type JobListResponse = {
  items: JobListItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

export type JobSearchParams = {
  q?: string;
  location?: string;
  workplace_type?: string;
  employment_type?: string;
  company?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  is_active?: boolean;
  source?: string;
  page?: number;
  page_size?: number;
};

export type JobCreatePayload = {
  title: string;
  company_name: string;
  description?: string;
  location?: string;
  employment_type?: string;
  workplace_type?: string;
  source_url?: string;
  skills?: string[];
};

export type IngestResponse = {
  source: string;
  fetched: number;
  inserted: number;
  updated: number;
  duplicates: number;
  failed: number;
  errors: string[];
};

export type JobSource = {
  id: string;
  name: string;
  source_type: string;
  external_key: string | null;
  base_url: string | null;
  is_active: boolean;
  current_fetch_datetime: string | null;
  last_fetch_datetime: string | null;
  created_at: string;
  updated_at: string;
};

export type JobSourceCreatePayload = {
  url?: string;
  source_type?: "greenhouse" | "lever";
  token?: string;
  name?: string;
  fetch_now?: boolean;
};

export type JobSourceCreateResponse = JobSource & {
  ingest: IngestResponse | null;
};

export type JobFetchRun = {
  id: string;
  current_fetch_datetime: string;
  last_fetch_datetime: string | null;
  finished_at: string | null;
  status: string;
  boards_attempted: number;
  boards_succeeded: number;
  fetched: number;
  inserted: number;
  updated: number;
  duplicates: number;
  failed: number;
  errors: string[];
};
