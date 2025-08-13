import { toast } from "sonner";

export function notifySuccess(message: string) {
  toast.success(message);
}

export function notifyInfo(message: string) {
  toast.info(message);
}

export function notifyError(error: unknown, fallback: string = "Operation failed") {
  const message = error instanceof Error ? error.message : fallback;
  toast.error(message);
}
