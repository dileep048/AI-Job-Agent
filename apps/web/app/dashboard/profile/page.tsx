import { ProfileNav } from "@/components/layout/ProfileNav";
import { ProfileForm } from "@/components/profile/ProfileForm";

export default function ProfilePage() {
  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold">Profile</h1>
      <ProfileNav />
      <ProfileForm />
    </div>
  );
}
