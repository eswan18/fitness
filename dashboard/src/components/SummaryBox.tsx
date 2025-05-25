import { Card, CardContent, CardTitle } from "./ui/card";

export interface SummaryBoxProps {
  title: string;
  value: string | number;
  size: "sm" | "md" | "lg";
  className?: string;
}
export function SummaryBox(
  { title, value, size = "md", className }: SummaryBoxProps,
) {
  const sizeClasses = {
    sm: "w-40 h-16 py-2",
    md: "w-64 h-24 py-3",
    lg: "w-96 h-36 py-5",
  }[size];
  const cardClasses =
    `bg-muted ${sizeClasses} shadow-none border-none ${className}`;
  const cardContentClasses = "flex flex-col items-start justify-evenly h-full";
  const valueSizeClasses = {
    sm: "text-xl",
    md: "text-3xl",
    lg: "text-5xl",
  }[size];
  const valueClasses = `text-foreground font-bold ${valueSizeClasses}`;
  const titleSizeClasses = {
    sm: "text-xs",
    md: "text-base",
    lg: "text-xl",
  }[size];
  const titleClasses = `text-muted-foreground ${titleSizeClasses}`;
  return (
    <Card className={cardClasses}>
      <CardContent className={cardContentClasses}>
        <CardTitle className={titleClasses}>{title}</CardTitle>
        <div className={valueClasses}>{value}</div>
      </CardContent>
    </Card>
  );
}
