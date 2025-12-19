import { useState } from "react";
import { WelcomeModal } from "./WelcomeModal";
import { oauthAuthorizeUrl } from "@/lib/auth";


interface AuthGateProps {
  children: React.ReactNode;
}

export function AuthGate({ children }: AuthGateProps) {
  const [showContent, setShowContent] = useState(false);

  // Don't render AuthGate UI if we're on the OAuth callback route
  // (OAuthCallbackHandler will handle that)
  if (window.location.pathname === "/oauth/callback") {
    return null;
  }

  return (
    <>
      {showContent ? (
        children
      ) : (
        <div className="min-h-screen bg-background" />
      )}
      <WelcomeModal
        open={!showContent}
        onLogin={() => {
          window.location.href = oauthAuthorizeUrl();
        }}
        onGuest={() => setShowContent(true)}
      />
    </>
  );
}
