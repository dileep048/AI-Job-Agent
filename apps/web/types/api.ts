export type User = {
  id: string;
  email: string;
  name: string | null;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Profile = {
  id: string;
  user_id: string;
  headline: string | null;
  summary: string | null;
  years_experience: number | null;
  current_role: string | null;
  current_company: string | null;
  preferred_locations: string[];
  preferred_job_types: string[];
  minimum_salary: number | null;
  maximum_salary: number | null;
  salary_currency: string;
  remote_preference: string | null;
  created_at: string;
  updated_at: string;
};

export type Skill = {
  id: string;
  profile_id: string;
  skill_name: string;
  skill_type: string | null;
  years_experience: number | null;
  proficiency: string | null;
  created_at: string;
  updated_at: string;
};

export type Experience = {
  id: string;
  profile_id: string;
  company_name: string;
  job_title: string;
  start_date: string;
  end_date: string | null;
  description: string | null;
  achievements: string[];
  technologies: string[];
  created_at: string;
  updated_at: string;
};

export type Education = {
  id: string;
  profile_id: string;
  institution: string;
  degree: string | null;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type ResumeData = {
  summary: string;
  skills: unknown[];
  experience: unknown[];
  education: unknown[];
  projects: unknown[];
};

export type Resume = {
  id: string;
  user_id: string;
  name: string;
  version: number;
  resume_data: ResumeData;
  file_url: string | null;
  file_name: string | null;
  file_type: string | null;
  file_size: number | null;
  is_default: boolean;
  status: string;
  created_at: string;
  updated_at: string;
};
