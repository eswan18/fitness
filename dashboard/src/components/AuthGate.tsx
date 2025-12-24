import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { WelcomeModal } from "./WelcomeModal";
import { oauthAuthorizeUrl } from "@/lib/auth";
import { useDashboardStore } from "@/store";

interface AuthGateProps {
  children: React.ReactNode;
}

export function AuthGate({ children }: AuthGateProps) {
  const { isAuthenticated } = useDashboardStore();
  const location = useLocation();
  const [showContent, setShowContent] = useState(false);

  // If user is authenticated (via OAuth or other means), show content immediately
  useEffect(() => {
    if (isAuthenticated) {
      setShowContent(true);
    }
  }, [isAuthenticated]);

  // Don't render AuthGate UI if we're on the OAuth callback route
  // (OAuthCallbackHandler will handle that)
  if (location.pathname === "/oauth/callback") {
    return null;
  }

  // Show content if authenticated or if user chose guest mode
  const shouldShowContent = isAuthenticated || showContent;

  return (
    <>
      {shouldShowContent ? (
        children
      ) : (
        <div className="min-h-screen bg-background" />
      )}
      <WelcomeModal
        open={!shouldShowContent}
        onLogin={async () => {
          const authUrl = await oauthAuthorizeUrl();
          window.location.href = authUrl;
        }}
        onGuest={() => setShowContent(true)}
      />
    </>
  );
}
