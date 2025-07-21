import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import type { ShoeMileageWithRetirement } from "@/lib/api";
import { Settings } from "lucide-react";
import { ShoeManagementDialog } from "@/components/ShoeManagementDialog";

const chartConfig = {
  mileage: {
    label: "Mileage",
    color: "hsl(var(--primary))",
  },
  retiredMileage: {
    label: "Retired Mileage", 
    color: "hsl(var(--muted-foreground))",
  },
} satisfies ChartConfig;

export function ShoeMileageChart({ data }: { data: ShoeMileageWithRetirement[] }) {
  const [sortKey, setSortKey] = useState<"mileage" | "shoe">("mileage");
  const [excludeLowMileage, setExcludeLowMileage] = useState(true);
  const [includeRetired, setIncludeRetired] = useState(false);
  const [managementDialogOpen, setManagementDialogOpen] = useState(false);

  const chartData = useMemo(() => {
    return [...data]
      .filter((d) => includeRetired || !d.retired) // Filter by retirement status
      .filter((d) => !excludeLowMileage || d.mileage >= 100)
      .sort((a, b) =>
        sortKey === "mileage"
          ? b.mileage - a.mileage
          : a.shoe.localeCompare(b.shoe),
      )
      .map((d) => ({
        shoe: d.shoe,
        mileage: d.mileage,
        retired: d.retired,
        retirement_date: d.retirement_date,
        retirement_notes: d.retirement_notes,
      }));
  }, [data, sortKey, excludeLowMileage, includeRetired]);
  return (
    <div className="w-full flex flex-col gap-y-4">
      <div className="px-8 py-2 flex flex-wrap items-start gap-4 w-full">
        <div className="flex flex-col gap-y-1 min-w-fit">
          <Label
            htmlFor="sort-select"
            className="text-sm font-medium"
          >
            Sort By
          </Label>
          <Select
            value={sortKey}
            onValueChange={(val) => setSortKey(val as "mileage" | "shoe")}
          >
            <SelectTrigger id="sort-select" className="w-32">
              <SelectValue placeholder="Select sort key" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="mileage">Mileage</SelectItem>
              <SelectItem value="shoe">Shoe Name</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex flex-col gap-y-1 min-w-fit">
          <Label
            htmlFor="include-retired-switch"
            className="text-sm font-medium"
          >
            Retired shoes
          </Label>
          <div className="flex flex-row items-center gap-x-2 h-9">
            <Label htmlFor="include-retired-switch" className="text-foreground text-sm">
              Include
            </Label>
            <Switch
              id="include-retired-switch"
              checked={includeRetired}
              onCheckedChange={setIncludeRetired}
            />
          </div>
        </div>
        
        <div className="flex flex-col gap-y-1 min-w-fit">
          <Label
            htmlFor="exclude-switch"
            className="text-sm font-medium"
          >
            Under 100 miles
          </Label>
          <div className="flex flex-row items-center gap-x-2 h-9">
            <Label htmlFor="exclude-switch" className="text-foreground text-sm">
              Exclude
            </Label>
            <Switch
              id="exclude-switch"
              checked={excludeLowMileage}
              onCheckedChange={setExcludeLowMileage}
            />
          </div>
        </div>
        
        <div className="flex flex-col gap-y-1 min-w-fit">
          <Label className="text-sm font-medium">
            Manage
          </Label>
          <Button
            variant="outline"
            size="sm"
            className="h-9"
            onClick={() => setManagementDialogOpen(true)}
          >
            <Settings className="h-4 w-4 mr-1" />
            Shoes
          </Button>
        </div>
      </div>
      <ChartContainer
        config={chartConfig}
        className="w-full max-w-xl mx-auto min-h-108"
      >
        <BarChart
          accessibilityLayer
          data={chartData}
          layout="vertical"
          margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
          height={800}
        >
          <ReferenceLine
            x={300}
            stroke="var(--destructive)"
            strokeDasharray="4 2"
            opacity={0.3}
          />
          <ReferenceLine
            x={500}
            stroke="var(--destructive)"
            strokeDasharray="4 2"
          />
          <CartesianGrid strokeDasharray="3 4" horizontal={false} />
          <XAxis type="number" ticks={[0, 100, 200, 300, 400, 500]} />
          <YAxis
            type="category"
            dataKey="shoe"
            width={120}
            tick={{ fontSize: 10 }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar dataKey="mileage" radius={4}>
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.retired ? "hsl(var(--muted-foreground))" : "hsl(var(--primary))"}
                opacity={entry.retired ? 0.6 : 1}
              />
            ))}
          </Bar>
        </BarChart>
      </ChartContainer>
      
      <ShoeManagementDialog
        shoes={data}
        open={managementDialogOpen}
        onOpenChange={setManagementDialogOpen}
      />
    </div>
  );
}
