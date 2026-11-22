import { ProfileNav } from "@/components/layout/ProfileNav";
import { EducationManager } from "@/components/profile/EducationManager";

export default function EducationPage() {
  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold">Education</h1>
      <ProfileNav />
      <EducationManager />
    </div>
  );
}
