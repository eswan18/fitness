import { useState } from "react";
import { useDashboardStore } from "@/store";
import { WelcomeModal } from "./WelcomeModal";
import { LoginFormModal } from "./LoginFormModal";

interface AuthGateProps {
  children: React.ReactNode;
}

export function AuthGate({ children }: AuthGateProps) {
  const { isAuthenticated } = useDashboardStore();
  const [showWelcome, setShowWelcome] = useState(!isAuthenticated);
  const [showLoginForm, setShowLoginForm] = useState(false);

  return (
    <>
      {children}
      <WelcomeModal
        open={showWelcome}
        onLogin={() => {
          setShowWelcome(false);
          setShowLoginForm(true);
        }}
        onGuest={() => setShowWelcome(false)}
      />
      <LoginFormModal
        open={showLoginForm}
        onSuccess={() => setShowLoginForm(false)}
        onCancel={() => setShowLoginForm(false)}
      />
    </>
  );
}
