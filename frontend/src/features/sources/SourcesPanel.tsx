import React from "react";
import type { Citation, Snippet } from "../../types/api";
import { useChatContext } from "../../contexts/ChatContext";

const SourcesPanel: React.FC = () => {
  const { lastResponse } = useChatContext();

  // If no lastResponse, show placeholder text
  if (!lastResponse) {
    return (
      <>
        <header>
          <div className="app-heading">Sources</div>
          <div className="muted">Cited items and snippets.</div>
        </header>
        <main>
          <div className="muted">
            This panel will show cited items and supporting snippets from your Zotero
            PDFs once you ask a question.
          </div>
        </main>
      </>
    );
  }

  // Render actual sources from lastResponse
  return (
    <>
      <header>
        <div className="app-heading">Sources</div>
        <div className="muted">Cited items and snippets.</div>
      </header>
      <main>
        <div style={{ marginBottom: 8 }} className="muted">
          Showing sources for the last answer.
        </div>
        <div>
          <h4>Summary</h4>
          <div>{lastResponse.summary}</div>
        </div>
        <div style={{ marginTop: 12 }}>
          <h4>Citations</h4>
          <ul>
            {lastResponse.citations.map((c) => (
              <li key={c.id}>{c.title} ({c.year ?? "n.d."})</li>
            ))}
          </ul>
        </div>
        <div style={{ marginTop: 12 }}>
          <h4>Snippets</h4>
          <ul>
            {lastResponse.snippets.map((s) => (
              <li key={s.id}>{s.text}</li>
            ))}
          </ul>
        </div>
      </main>
    </>
  );
};

export default SourcesPanel;
