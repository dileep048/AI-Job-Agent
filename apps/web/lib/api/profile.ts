import { apiRequest } from "@/lib/api/client";
import type { Education, Experience, Profile, Skill } from "@/types/api";

export function getProfile() {
  return apiRequest<Profile>("/api/v1/profile");
}

export function createProfile(payload: Partial<Profile>) {
  return apiRequest<Profile>("/api/v1/profile", { method: "POST", body: payload });
}

export function updateProfile(payload: Partial<Profile>) {
  return apiRequest<Profile>("/api/v1/profile", { method: "PUT", body: payload });
}

export function listSkills() {
  return apiRequest<Skill[]>("/api/v1/profile/skills");
}

export function createSkill(payload: Partial<Skill>) {
  return apiRequest<Skill>("/api/v1/profile/skills", { method: "POST", body: payload });
}

export function updateSkill(id: string, payload: Partial<Skill>) {
  return apiRequest<Skill>(`/api/v1/profile/skills/${id}`, { method: "PUT", body: payload });
}

export function deleteSkill(id: string) {
  return apiRequest<void>(`/api/v1/profile/skills/${id}`, { method: "DELETE" });
}

export function listExperience() {
  return apiRequest<Experience[]>("/api/v1/profile/experience");
}

export function createExperience(payload: Partial<Experience> & { currently_working?: boolean }) {
  return apiRequest<Experience>("/api/v1/profile/experience", { method: "POST", body: payload });
}

export function updateExperience(
  id: string,
  payload: Partial<Experience> & { currently_working?: boolean },
) {
  return apiRequest<Experience>(`/api/v1/profile/experience/${id}`, {
    method: "PUT",
    body: payload,
  });
}

export function deleteExperience(id: string) {
  return apiRequest<void>(`/api/v1/profile/experience/${id}`, { method: "DELETE" });
}

export function listEducation() {
  return apiRequest<Education[]>("/api/v1/profile/education");
}

export function createEducation(payload: Partial<Education>) {
  return apiRequest<Education>("/api/v1/profile/education", { method: "POST", body: payload });
}

export function updateEducation(id: string, payload: Partial<Education>) {
  return apiRequest<Education>(`/api/v1/profile/education/${id}`, {
    method: "PUT",
    body: payload,
  });
}

export function deleteEducation(id: string) {
  return apiRequest<void>(`/api/v1/profile/education/${id}`, { method: "DELETE" });
}
