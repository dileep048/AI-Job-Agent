import { apiRequest } from "@/lib/api/client";
import type { JobMatch, JobMatchListResponse } from "@/types/matches";

export function getJobMatch(jobId: string) {
  return apiRequest<JobMatch>(`/api/v1/jobs/${jobId}/match`);
}

export function scoreJob(jobId: string) {
  return apiRequest<JobMatch>(`/api/v1/jobs/${jobId}/match`, { method: "POST" });
}

export function listMatches(params?: { page?: number; page_size?: number; min_score?: number }) {
  const search = new URLSearchParams();
  if (params?.page) search.set("page", String(params.page));
  if (params?.page_size) search.set("page_size", String(params.page_size));
  if (params?.min_score != null) search.set("min_score", String(params.min_score));
  const query = search.toString();
  return apiRequest<JobMatchListResponse>(`/api/v1/matches${query ? `?${query}` : ""}`);
}

export function scoreJobs(jobIds: string[]) {
  return apiRequest<JobMatch[]>("/api/v1/matches/jobs", { method: "POST", body: { job_ids: jobIds } });
}

export function refreshMatches(limit = 50) {
  return apiRequest<JobMatch[]>("/api/v1/matches/refresh", { method: "POST", body: { limit } });
}
