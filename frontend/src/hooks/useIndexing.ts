import { useEffect, useState } from "react";
import { indexLibrary, getIndexStatus, cancelIndexing } from "../api";

type Status = "idle" | "indexing" | "done" | "error";

export function useIndexing() {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<{ processed_items?: number; total_items?: number } | null>(null);

  async function startIndexing() {
    setError(null);
    setStatus("indexing");
    try {
      await indexLibrary();
      // backend can immediately set status; we poll below
    } catch (e: any) {
      setStatus("error");
      setError(e.message ?? "Failed to start indexing");
    }
  }

  async function cancel() {
    try {
      await cancelIndexing();
    } catch (e) {
      // ignore errors here
    }
  }

  useEffect(() => {
    let timer: number | undefined;

    async function poll() {
      try {
        const res = await getIndexStatus();
        if (res.status === "indexing") {
          setStatus("indexing");
        } else if (res.status === "done") {
          setStatus("done");
        } else {
          setStatus("idle");
        }
        if (res.progress) setProgress(res.progress as any);
      } catch {
        // ignore, stay in current state
      }
      timer = window.setTimeout(poll, 4000);
    }

    poll();
    return () => {
      if (timer) window.clearTimeout(timer);
    };
  }, []);

  return { status, error, startIndexing, cancel, progress };
}
