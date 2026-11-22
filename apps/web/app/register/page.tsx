import { RegisterForm } from "@/components/forms/RegisterForm";
import { AuthPageShell } from "@/components/layout/AuthPageShell";

export default function RegisterPage() {
  return (
    <AuthPageShell>
      <RegisterForm />
    </AuthPageShell>
  );
}
