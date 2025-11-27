import React from "react";
import { useIndexing } from "../../hooks/useIndexing";
import ThreadList from "./ThreadList";

function ProgressBar({ progress }: { progress?: { processed_items?: number; total_items?: number } | null }) {
  if (!progress || !progress.total_items) return null;
  const pct = Math.round(((progress.processed_items || 0) / (progress.total_items || 1)) * 100);
  return (
    <div style={{ marginTop: 8 }}>
      <div style={{ height: 10, background: "#eee", borderRadius: 6, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg,#e6c48b,#cfa86a)" }} />
      </div>
      <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>Progress: {pct}% ({progress.processed_items || 0}/{progress.total_items})</div>
    </div>
  );
}

const Sidebar: React.FC = () => {
  const { status, error, startIndexing, cancel, progress } = useIndexing();

  function label() {
    if (status === "indexing") return "Indexing…";
    if (status === "done") return "Reindex library";
    return "Index library";
  }

  return (
    <>
      <header>
        <div className="app-heading">Library</div>
        <div className="muted">Controls & future filters.</div>
      </header>
      <main>
        {error && <div className="error-banner">{error}</div>}
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button
            className="btn"
            onClick={startIndexing}
            disabled={status === "indexing"}
          >
            {label()}
          </button>
          {status === "indexing" && (
            <button className="btn" onClick={cancel}>
              Cancel
            </button>
          )}
        </div>
        <ProgressBar progress={progress} />
        <div style={{ marginTop: 8 }} className="status-pill">
          Status: {status}
        </div>

        <div style={{ marginTop: 16 }}>
          <ThreadList />
        </div>
      </main>
    </>
  );
};

export default Sidebar;
