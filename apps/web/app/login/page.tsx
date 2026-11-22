import { LoginForm } from "@/components/forms/LoginForm";
import { AuthPageShell } from "@/components/layout/AuthPageShell";

export default function LoginPage() {
  return (
    <AuthPageShell>
      <LoginForm />
    </AuthPageShell>
  );
}
