import { ProfileNav } from "@/components/layout/ProfileNav";
import { ExperienceManager } from "@/components/profile/ExperienceManager";

export default function ExperiencePage() {
  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold">Experience</h1>
      <ProfileNav />
      <ExperienceManager />
    </div>
  );
}
