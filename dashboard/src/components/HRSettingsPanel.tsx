import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useDashboardStore } from "@/store";
import { Settings } from "lucide-react";

interface HRSettingsPanelProps {
  className?: string;
}

export function HRSettingsPanel({ className }: HRSettingsPanelProps) {
  const { maxHr, setMaxHr, restingHr, setRestingHr, sex, setSex } = useDashboardStore();
  
  // Local state for input values to handle validation
  const [localMaxHr, setLocalMaxHr] = useState(maxHr.toString());
  const [localRestingHr, setLocalRestingHr] = useState(restingHr.toString());
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const handleMaxHrChange = (value: string) => {
    setLocalMaxHr(value);
    setHasUnsavedChanges(true);
  };

  const handleRestingHrChange = (value: string) => {
    setLocalRestingHr(value);
    setHasUnsavedChanges(true);
  };

  const handleSexChange = (value: "M" | "F") => {
    setSex(value);
    // Sex changes are applied immediately
  };

  const handleSave = () => {
    const maxHrNum = parseInt(localMaxHr);
    const restingHrNum = parseInt(localRestingHr);

    // Validation
    if (isNaN(maxHrNum) || maxHrNum < 100 || maxHrNum > 250) {
      alert("Max HR must be between 100 and 250 bpm");
      return;
    }

    if (isNaN(restingHrNum) || restingHrNum < 30 || restingHrNum > 100) {
      alert("Resting HR must be between 30 and 100 bpm");
      return;
    }

    if (restingHrNum >= maxHrNum) {
      alert("Resting HR must be less than Max HR");
      return;
    }

    setMaxHr(maxHrNum);
    setRestingHr(restingHrNum);
    setHasUnsavedChanges(false);
  };

  const handleReset = () => {
    setLocalMaxHr(maxHr.toString());
    setLocalRestingHr(restingHr.toString());
    setHasUnsavedChanges(false);
  };

  return (
    <Card className={`p-4 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <Settings className="h-4 w-4" />
        <h3 className="font-medium">Heart Rate Settings</h3>
      </div>
      
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="maxHr">Max HR (bpm)</Label>
          <Input
            id="maxHr"
            type="number"
            value={localMaxHr}
            onChange={(e) => handleMaxHrChange(e.target.value)}
            min="100"
            max="250"
            className="w-full"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="restingHr">Resting HR (bpm)</Label>
          <Input
            id="restingHr"
            type="number"
            value={localRestingHr}
            onChange={(e) => handleRestingHrChange(e.target.value)}
            min="30"
            max="100"
            className="w-full"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="sex">Sex</Label>
          <Select value={sex} onValueChange={handleSexChange}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="M">Male</SelectItem>
              <SelectItem value="F">Female</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {hasUnsavedChanges && (
          <div className="flex gap-2 pt-2">
            <Button onClick={handleSave} size="sm">
              Save Changes
            </Button>
            <Button onClick={handleReset} variant="outline" size="sm">
              Reset
            </Button>
          </div>
        )}
      </div>
      
      <p className="text-xs text-muted-foreground mt-3">
        These settings affect TRIMP calculations and training load analysis.
      </p>
    </Card>
  );
}