import { useEnvironment } from "@/lib/useEnvironment";
import { Badge } from "./ui/badge";

export function EnvironmentIndicator() {
  const { data: environment, isPending, error } = useEnvironment();

  if (isPending) return null;
  if (error) return null;

  const env = environment?.environment || "unknown";

  // Determine colors based on environment
  const getVariant = (env: string) => {
    switch (env.toLowerCase()) {
      case "prod":
      case "production":
        return "destructive"; // Red for production
      case "dev":
      case "development":
        return "default"; // Primary color for development (more eye-catching)
      default:
        return "outline"; // Default for unknown
    }
  };

  return (
    <Badge variant={getVariant(env)} className="text-xs font-medium">
      {env.toUpperCase()}
    </Badge>
  );
}
