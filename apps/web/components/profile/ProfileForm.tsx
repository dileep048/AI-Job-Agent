"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api/client";
import { createProfile, getProfile, updateProfile } from "@/lib/api/profile";
import { useToast } from "@/providers/ToastProvider";

const schema = z.object({
  name: z.string().optional(),
  email: z.string().email(),
  headline: z.string().optional(),
  current_role: z.string().optional(),
  current_company: z.string().optional(),
  years_experience: z.coerce.number().min(0).max(80).optional(),
  summary: z.string().optional(),
  preferred_locations: z.string().optional(),
  preferred_job_types: z.string().optional(),
  remote_preference: z.string().optional(),
  minimum_salary: z.coerce.number().min(0).optional(),
  maximum_salary: z.coerce.number().min(0).optional(),
  salary_currency: z.string().default("INR"),
});

type FormValues = z.infer<typeof schema>;

function csv(value: string | undefined): string[] {
  return (value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function ProfileForm() {
  const { user } = useAuth();
  const toast = useToast();
  const queryClient = useQueryClient();
  const profileQuery = useQuery({ queryKey: ["profile"], queryFn: getProfile, retry: false });

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    values: {
      name: user?.name ?? "",
      email: user?.email ?? "",
      headline: profileQuery.data?.headline ?? "",
      current_role: profileQuery.data?.current_role ?? "",
      current_company: profileQuery.data?.current_company ?? "",
      years_experience: profileQuery.data?.years_experience ?? undefined,
      summary: profileQuery.data?.summary ?? "",
      preferred_locations: profileQuery.data?.preferred_locations.join(", ") ?? "",
      preferred_job_types: profileQuery.data?.preferred_job_types.join(", ") ?? "",
      remote_preference: profileQuery.data?.remote_preference ?? "hybrid",
      minimum_salary: profileQuery.data?.minimum_salary ?? undefined,
      maximum_salary: profileQuery.data?.maximum_salary ?? undefined,
      salary_currency: profileQuery.data?.salary_currency ?? "INR",
    },
  });

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const payload = {
        headline: values.headline || null,
        summary: values.summary || null,
        years_experience: values.years_experience ?? null,
        current_role: values.current_role || null,
        current_company: values.current_company || null,
        preferred_locations: csv(values.preferred_locations),
        preferred_job_types: csv(values.preferred_job_types),
        minimum_salary: values.minimum_salary ?? null,
        maximum_salary: values.maximum_salary ?? null,
        salary_currency: values.salary_currency,
        remote_preference: values.remote_preference || null,
      };
      const missing =
        profileQuery.error instanceof ApiError && profileQuery.error.status === 404;
      if (missing) return createProfile(payload);
      return updateProfile(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      toast.notify("Profile saved");
    },
    onError: (error) => {
      toast.notify(error instanceof Error ? error.message : "Could not save profile", "error");
    },
  });

  if (profileQuery.isLoading) return <Spinner />;

  return (
    <form className="space-y-6" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <Card>
        <h2 className="text-lg font-semibold">Basic Information</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Input label="Name" {...form.register("name")} disabled />
          <Input label="Email" {...form.register("email")} disabled />
          <Input label="Headline" {...form.register("headline")} />
          <Input label="Current Role" {...form.register("current_role")} />
          <Input label="Current Company" {...form.register("current_company")} />
          <Input
            label="Years of Experience"
            type="number"
            {...form.register("years_experience")}
          />
        </div>
        <div className="mt-4">
          <Textarea label="Summary" {...form.register("summary")} />
        </div>
      </Card>
      <Card>
        <h2 className="text-lg font-semibold">Job Preferences</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Input
            label="Preferred Locations"
            placeholder="Bengaluru, Remote"
            {...form.register("preferred_locations")}
          />
          <Input
            label="Job Types"
            placeholder="full-time, contract"
            {...form.register("preferred_job_types")}
          />
          <Select label="Remote Preference" {...form.register("remote_preference")}>
            <option value="remote">Remote</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">Onsite</option>
            <option value="any">Any</option>
          </Select>
          <Select label="Currency" {...form.register("salary_currency")}>
            <option value="INR">INR</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
          </Select>
          <Input label="Minimum Salary" type="number" {...form.register("minimum_salary")} />
          <Input label="Maximum Salary" type="number" {...form.register("maximum_salary")} />
        </div>
      </Card>
      {form.formState.errors.email ? (
        <ErrorState message={form.formState.errors.email.message ?? "Invalid form"} />
      ) : null}
      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "Saving..." : "Save profile"}
      </Button>
    </form>
  );
}
