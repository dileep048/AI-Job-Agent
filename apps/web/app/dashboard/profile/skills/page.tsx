import { ProfileNav } from "@/components/layout/ProfileNav";
import { SkillsManager } from "@/components/profile/SkillsManager";

export default function SkillsPage() {
  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold">Skills</h1>
      <ProfileNav />
      <SkillsManager />
    </div>
  );
}
