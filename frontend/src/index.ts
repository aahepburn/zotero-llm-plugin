// src/index.ts

import { registerChatTab } from "./chatTab";

function startup() {
  registerChatTab();
}

function shutdown() {
  // If you used a toolkit helper, call its unregister here if needed.
}

export { startup, shutdown };
