import { apiRequest, downloadAuthorized } from "@/lib/api/client";
import type { Resume, ResumeData } from "@/types/api";

export function listResumes() {
  return apiRequest<Resume[]>("/api/v1/resumes");
}

export function getResume(id: string) {
  return apiRequest<Resume>(`/api/v1/resumes/${id}`);
}

export function updateResume(id: string, payload: { name?: string; resume_data?: ResumeData }) {
  return apiRequest<Resume>(`/api/v1/resumes/${id}`, { method: "PUT", body: payload });
}

export function deleteResume(id: string) {
  return apiRequest<void>(`/api/v1/resumes/${id}`, { method: "DELETE" });
}

export function setDefaultResume(id: string) {
  return apiRequest<Resume>(`/api/v1/resumes/${id}/set-default`, { method: "POST" });
}

export function uploadResume(file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiRequest<Resume>("/api/v1/resumes/upload", { method: "POST", formData: form });
}

export function downloadResume(resume: Resume) {
  return downloadAuthorized(`/api/v1/resumes/${resume.id}/download`, resume.file_name ?? "resume");
}
