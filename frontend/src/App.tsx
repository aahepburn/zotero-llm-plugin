// src/App.tsx
import React from "react";
import AppShell from "./components/layout/AppShell";
import "./styles/globals.css";
import "./styles/theme.css";
import { ChatProvider } from "./contexts/ChatContext";

const App: React.FC = () => (
	<ChatProvider>
		<AppShell />
	</ChatProvider>
);

export default App;
