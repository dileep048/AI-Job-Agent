import type { JobListItem } from "@/types/jobs";

export type JobMatch = {
  id: string;
  job_id: string;
  overall_score: number;
  skill_score: number;
  experience_score: number;
  location_score: number;
  salary_score: number;
  semantic_score: number;
  recommendation: string;
  matched_skills: string[];
  missing_skills: string[];
  requirements: Record<string, unknown>;
  breakdown: Record<string, unknown>;
  explanation: string;
  explanation_source: string;
  created_at: string;
  updated_at: string;
  job: JobListItem | null;
};

export type JobMatchListResponse = {
  items: JobMatch[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};
