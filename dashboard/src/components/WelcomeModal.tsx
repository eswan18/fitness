import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface WelcomeModalProps {
  open: boolean;
  onLogin: () => void;
  onGuest: () => void;
}

export function WelcomeModal({ open, onLogin, onGuest }: WelcomeModalProps) {
  return (
    <Dialog open={open} onOpenChange={(open) => !open && onGuest()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Welcome to Running Dashboard</DialogTitle>
          <DialogDescription>
            Log in to edit runs and manage your data, or continue as a guest to
            view read-only.
          </DialogDescription>
        </DialogHeader>
        <div className="flex gap-3">
          <Button onClick={onLogin} className="flex-1">
            Log In
          </Button>
          <Button onClick={onGuest} variant="outline" className="flex-1">
            Continue as Guest
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
