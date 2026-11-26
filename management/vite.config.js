import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The panel talks to the game's backend (port 8001) through Vite's proxy, so no CORS setup is needed:
// /api/v1/admin/* is the management API and /assets/* serves the game's images.
const BACKEND = process.env.RCS_BACKEND || "http://127.0.0.1:8001";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": BACKEND,
      "/assets": BACKEND,
    },
  },
});
