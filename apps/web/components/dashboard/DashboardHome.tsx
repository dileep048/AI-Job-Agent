"use client";

import { ApiError } from "@/lib/api/client";
import { greeting } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorState } from "@/components/ui/ErrorState";
import { useAuth } from "@/hooks/useAuth";
import { getProfile, listEducation, listExperience, listSkills } from "@/lib/api/profile";
import { listResumes } from "@/lib/api/resume";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

function completion(parts: boolean[]): number {
  if (!parts.length) return 0;
  return Math.round((parts.filter(Boolean).length / parts.length) * 100);
}

export function DashboardHome() {
  const { user } = useAuth();
  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
    retry: false,
  });
  const skillsQuery = useQuery({ queryKey: ["skills"], queryFn: listSkills, retry: false });
  const experienceQuery = useQuery({
    queryKey: ["experience"],
    queryFn: listExperience,
    retry: false,
  });
  const educationQuery = useQuery({
    queryKey: ["education"],
    queryFn: listEducation,
    retry: false,
  });
  const resumesQuery = useQuery({ queryKey: ["resumes"], queryFn: listResumes });

  const loading =
    profileQuery.isLoading ||
    skillsQuery.isLoading ||
    experienceQuery.isLoading ||
    educationQuery.isLoading ||
    resumesQuery.isLoading;

  if (loading) return <Spinner />;

  const profileMissing =
    profileQuery.error instanceof ApiError && profileQuery.error.status === 404;
  const profile = profileQuery.data;
  const skills = skillsQuery.data ?? [];
  const experience = experienceQuery.data ?? [];
  const education = educationQuery.data ?? [];
  const resumes = resumesQuery.data ?? [];
  const defaultResume = resumes.find((item) => item.is_default) ?? resumes[0];

  const percent = completion([
    Boolean(user?.name),
    Boolean(profile?.headline),
    Boolean(profile?.summary),
    Boolean(profile?.current_role),
    skills.length > 0,
    experience.length > 0,
    education.length > 0,
    resumes.length > 0,
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">
          {greeting()} 👋
        </h1>
        <p className="mt-1 text-sm text-muted">
          {user?.name ? `Welcome back, ${user.name}.` : "Your job search workspace is ready."}
        </p>
      </div>

      {profileQuery.error && !profileMissing ? (
        <ErrorState message="Could not load your profile." />
      ) : null}

      <Card>
        <p className="text-sm font-medium">Profile completion</p>
        <p className="mt-2 text-2xl font-semibold">{percent}%</p>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-ai-light">
          <div className="h-full rounded-full bg-[#FACC15]" style={{ width: `${percent}%` }} />
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <p className="text-sm text-muted">Resume</p>
          <p className="mt-2 text-lg font-semibold">{defaultResume?.name ?? "No resume yet"}</p>
          {defaultResume ? (
            <Link className="mt-3 inline-block text-sm font-medium text-ink underline decoration-[#FACC15] decoration-2 underline-offset-4" href={`/dashboard/resumes/${defaultResume.id}`}>
              View Resume
            </Link>
          ) : (
            <Link className="mt-3 inline-block text-sm font-medium text-ink underline decoration-[#FACC15] decoration-2 underline-offset-4" href="/dashboard/resumes">
              Upload Resume
            </Link>
          )}
        </Card>
        <Card>
          <p className="text-sm text-muted">Profile</p>
          <p className="mt-2 text-sm">Experience: {profile?.years_experience ?? 0} years</p>
          <p className="text-sm">Skills: {skills.length}</p>
          <p className="text-sm">Education: {education.length}</p>
          <Link className="mt-3 inline-block text-sm font-medium text-ink underline decoration-[#FACC15] decoration-2 underline-offset-4" href="/dashboard/profile">
            Edit profile
          </Link>
        </Card>
        <Card className="bg-ai-light/60">
          <p className="text-sm font-medium text-ink">AI Agent</p>
          <p className="mt-1 text-sm text-muted">Coming soon</p>
          <ul className="mt-2 space-y-1 text-sm">
            <li>AI Job Matching</li>
            <li>Automatic Applications</li>
            <li>Application Tracking</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
