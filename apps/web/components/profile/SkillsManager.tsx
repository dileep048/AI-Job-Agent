"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { createSkill, deleteSkill, listSkills, updateSkill } from "@/lib/api/profile";
import { useToast } from "@/providers/ToastProvider";
import type { Skill } from "@/types/api";

const schema = z.object({
  skill_name: z.string().min(1, "Skill is required"),
  skill_type: z.string().optional(),
  years_experience: z.coerce.number().min(0).max(80).optional(),
  proficiency: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function SkillsManager() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<Skill | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Skill | null>(null);
  const skillsQuery = useQuery({ queryKey: ["skills"], queryFn: listSkills, retry: false });
  const form = useForm<FormValues>({ resolver: zodResolver(schema) });

  const save = useMutation({
    mutationFn: (values: FormValues) =>
      editing ? updateSkill(editing.id, values) : createSkill(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      toast.notify(editing ? "Skill updated" : "Skill added");
      setEditing(null);
      form.reset({ skill_name: "", skill_type: "Backend", years_experience: undefined, proficiency: "Expert" });
    },
    onError: (error) => toast.notify(error instanceof Error ? error.message : "Failed", "error"),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteSkill(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      toast.notify("Skill deleted");
      setPendingDelete(null);
    },
  });

  if (skillsQuery.isLoading) return <Spinner />;
  if (skillsQuery.error) {
    return <ErrorState message="Create a profile before adding skills." />;
  }

  const skills = skillsQuery.data ?? [];

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-lg font-semibold">{editing ? "Edit Skill" : "Add Skill"}</h2>
        <form
          className="mt-4 grid gap-4 md:grid-cols-4"
          onSubmit={form.handleSubmit((values) => save.mutate(values))}
        >
          <Input label="Skill" placeholder="Python" {...form.register("skill_name")} error={form.formState.errors.skill_name?.message} />
          <Select label="Type" {...form.register("skill_type")}>
            <option value="Backend">Backend</option>
            <option value="Frontend">Frontend</option>
            <option value="Language">Language</option>
            <option value="Tool">Tool</option>
            <option value="Cloud">Cloud</option>
          </Select>
          <Input label="Years" type="number" {...form.register("years_experience")} />
          <Select label="Proficiency" {...form.register("proficiency")}>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
            <option value="Expert">Expert</option>
          </Select>
          <div className="md:col-span-4 flex gap-2">
            <Button type="submit" disabled={save.isPending}>
              {editing ? "Update" : "Add skill"}
            </Button>
            {editing ? (
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setEditing(null);
                  form.reset();
                }}
              >
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
      </Card>

      {skills.length === 0 ? (
        <EmptyState title="No skills yet" description="Add skills that should appear on customized resumes." />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {skills.map((skill) => (
            <Card key={skill.id} className="flex items-start justify-between">
              <div>
                <p className="font-medium">{skill.skill_name}</p>
                <p className="text-sm text-muted">
                  {skill.skill_type ?? "Skill"} · {skill.years_experience ?? 0} yrs · {skill.proficiency ?? "—"}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  onClick={() => {
                    setEditing(skill);
                    form.reset({
                      skill_name: skill.skill_name,
                      skill_type: skill.skill_type ?? "Backend",
                      years_experience: skill.years_experience ?? undefined,
                      proficiency: skill.proficiency ?? "Expert",
                    });
                  }}
                >
                  Edit
                </Button>
                <Button variant="danger" onClick={() => setPendingDelete(skill)}>
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete skill"
        description={`Remove ${pendingDelete?.skill_name}?`}
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && remove.mutate(pendingDelete.id)}
      />
    </div>
  );
}
