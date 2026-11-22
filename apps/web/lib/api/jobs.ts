import { apiRequest } from "@/lib/api/client";
import { buildJobSearchQuery } from "@/lib/api/jobSearchQuery";
import type {
  IngestResponse,
  Job,
  JobCreatePayload,
  JobFetchRun,
  JobListResponse,
  JobSearchParams,
  JobSource,
  JobSourceCreatePayload,
  JobSourceCreateResponse,
} from "@/types/jobs";

export function searchJobs(params: JobSearchParams) {
  return apiRequest<JobListResponse>(`/api/v1/jobs${buildJobSearchQuery(params)}`);
}

export function getJob(id: string) {
  return apiRequest<Job>(`/api/v1/jobs/${id}`);
}

export function createJob(payload: JobCreatePayload) {
  return apiRequest<Job>("/api/v1/jobs", { method: "POST", body: payload });
}

export function ingestJobs(payload: {
  source_id?: string;
  source_type?: string;
  configuration?: Record<string, unknown>;
}) {
  return apiRequest<IngestResponse>("/api/v1/jobs/ingest", { method: "POST", body: payload });
}

export function importJobFromUrl(url: string) {
  return apiRequest<IngestResponse>("/api/v1/jobs/from-url", { method: "POST", body: { url } });
}

export function ingestGreenhouseAndLever() {
  return apiRequest<JobFetchRun>("/api/v1/jobs/ingest/boards", { method: "POST" });
}

export function getLatestFetchRun() {
  return apiRequest<JobFetchRun | null>("/api/v1/jobs/fetch-runs/latest");
}

export function listJobSources() {
  return apiRequest<JobSource[]>("/api/v1/job-sources");
}

export function createJobSource(payload: JobSourceCreatePayload) {
  return apiRequest<JobSourceCreateResponse>("/api/v1/job-sources", { method: "POST", body: payload });
}

export function updateJobSource(id: string, payload: { is_active: boolean }) {
  return apiRequest<JobSource>(`/api/v1/job-sources/${id}`, { method: "PATCH", body: payload });
}
