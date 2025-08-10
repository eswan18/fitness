import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/LoadingSpinner";

interface PanelProps {
  title: string;
  className?: string;
  isLoading?: boolean;
  error?: unknown;
  actions?: React.ReactNode;
  children: React.ReactNode;
  bodyClassName?: string;
}

export function Panel({
  title,
  className,
  isLoading,
  error,
  actions,
  children,
  bodyClassName,
}: PanelProps) {
  if (isLoading) {
    return (
      <div className={cn("flex flex-col gap-y-4", className)}>
        <div className="flex justify-between items-start">
          <h2 className="text-xl font-semibold">{title}</h2>
          {actions}
        </div>
        <Card className="w-full shadow-none flex justify-center items-center py-12">
          <LoadingSpinner />
        </Card>
      </div>
    );
  }

  if (error) {
    const message = error instanceof Error ? error.message : String(error);
    return (
      <div className={cn("flex flex-col gap-y-4", className)}>
        <div className="flex justify-between items-start">
          <h2 className="text-xl font-semibold">{title}</h2>
          {actions}
        </div>
        <Card className="w-full shadow-none flex justify-center items-center py-6">
          <p className="text-destructive">Error: {message}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col gap-y-4", className)}>
      <div className="flex justify-between items-start">
        <h2 className="text-xl font-semibold">{title}</h2>
        {actions}
      </div>
      <div className={cn("flex flex-col gap-y-4", bodyClassName)}>
        {children}
      </div>
    </div>
  );
}
