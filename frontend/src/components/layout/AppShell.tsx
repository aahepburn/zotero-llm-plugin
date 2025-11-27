import React from "react";
import Sidebar from "../../features/sidebar/Sidebar";
import ChatView from "../../features/chat/ChatView";
import SourcesPanel from "../../features/sources/SourcesPanel";
import "../../styles/layout.css";

const AppShell: React.FC = () => {
  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar">
        <Sidebar />
      </aside>
      <main className="app-shell__main">
        <ChatView />
      </main>
      <section className="app-shell__sources">
        <SourcesPanel />
      </section>
    </div>
  );
};

export default AppShell;
