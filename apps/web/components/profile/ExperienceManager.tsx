"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import {
  createExperience,
  deleteExperience,
  listExperience,
  updateExperience,
} from "@/lib/api/profile";
import { useToast } from "@/providers/ToastProvider";
import type { Experience } from "@/types/api";

const schema = z.object({
  company_name: z.string().min(1),
  job_title: z.string().min(1),
  start_date: z.string().min(1),
  end_date: z.string().optional(),
  currently_working: z.boolean().optional(),
  description: z.string().optional(),
  achievements: z.array(z.object({ value: z.string() })),
  technologies: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function ExperienceManager() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<Experience | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Experience | null>(null);
  const query = useQuery({ queryKey: ["experience"], queryFn: listExperience, retry: false });
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { currently_working: false, achievements: [{ value: "" }] },
  });
  const achievements = useFieldArray({ control: form.control, name: "achievements" });
  const currentlyWorking = form.watch("currently_working");

  const save = useMutation({
    mutationFn: (values: FormValues) => {
      const payload = {
        company_name: values.company_name,
        job_title: values.job_title,
        start_date: values.start_date,
        end_date: values.currently_working ? null : values.end_date || null,
        currently_working: values.currently_working,
        description: values.description || null,
        achievements: values.achievements.map((item) => item.value).filter(Boolean),
        technologies: (values.technologies ?? "")
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
      };
      return editing ? updateExperience(editing.id, payload) : createExperience(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["experience"] });
      toast.notify(editing ? "Experience updated" : "Experience added");
      setEditing(null);
      form.reset({ currently_working: false, achievements: [{ value: "" }] });
    },
    onError: (error) => toast.notify(error instanceof Error ? error.message : "Failed", "error"),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteExperience(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["experience"] });
      toast.notify("Experience deleted");
      setPendingDelete(null);
    },
  });

  if (query.isLoading) return <Spinner />;
  if (query.error) return <ErrorState message="Create a profile before adding experience." />;

  const items = query.data ?? [];

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-lg font-semibold">{editing ? "Edit experience" : "Add experience"}</h2>
        <form className="mt-4 space-y-4" onSubmit={form.handleSubmit((values) => save.mutate(values))}>
          <div className="grid gap-4 md:grid-cols-2">
            <Input label="Company" {...form.register("company_name")} />
            <Input label="Job Title" {...form.register("job_title")} />
            <Input label="Start Date" type="date" {...form.register("start_date")} />
            <Input
              label="End Date"
              type="date"
              disabled={currentlyWorking}
              {...form.register("end_date")}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" {...form.register("currently_working")} />
            Currently working here
          </label>
          <Textarea label="Description" {...form.register("description")} />
          <div>
            <p className="mb-2 text-sm font-medium">Achievements</p>
            {achievements.fields.map((field, index) => (
              <div key={field.id} className="mb-2 flex gap-2">
                <Input placeholder="Migrated third-party integration..." {...form.register(`achievements.${index}.value`)} />
                <Button type="button" variant="ghost" onClick={() => achievements.remove(index)}>
                  Remove
                </Button>
              </div>
            ))}
            <Button type="button" variant="secondary" onClick={() => achievements.append({ value: "" })}>
              + Add achievement
            </Button>
          </div>
          <Input
            label="Technologies"
            placeholder="Python, FastAPI, PostgreSQL"
            {...form.register("technologies")}
          />
          <div className="flex gap-2">
            <Button type="submit">{editing ? "Update" : "Save experience"}</Button>
            {editing ? (
              <Button type="button" variant="secondary" onClick={() => setEditing(null)}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
      </Card>

      {items.length === 0 ? (
        <EmptyState title="No experience yet" description="Add roles you want the agent to reference." />
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <Card key={item.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold">
                    {item.job_title} · {item.company_name}
                  </p>
                  <p className="text-sm text-muted">
                    {item.start_date} — {item.end_date ?? "Present"}
                  </p>
                  {item.achievements.length ? (
                    <ul className="mt-2 list-disc pl-5 text-sm">
                      {item.achievements.map((achievement) => (
                        <li key={achievement}>{achievement}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setEditing(item);
                      form.reset({
                        company_name: item.company_name,
                        job_title: item.job_title,
                        start_date: item.start_date,
                        end_date: item.end_date ?? "",
                        currently_working: !item.end_date,
                        description: item.description ?? "",
                        achievements: item.achievements.length
                          ? item.achievements.map((value) => ({ value }))
                          : [{ value: "" }],
                        technologies: item.technologies.join(", "),
                      });
                    }}
                  >
                    Edit
                  </Button>
                  <Button variant="danger" onClick={() => setPendingDelete(item)}>
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete experience"
        description="This role will be removed from your profile."
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && remove.mutate(pendingDelete.id)}
      />
    </div>
  );
}
