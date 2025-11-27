/// <reference types="vitest" />
import path from "path";
import { defineConfig } from "vite";
import type { Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Plugin to handle /api/health endpoint with CORS
function healthEndpointPlugin(): Plugin {
  return {
    name: "health-endpoint",
    configureServer(server) {
      server.middlewares.use("/api/health", (req, res, next) => {
        // Set CORS headers only for this endpoint
        res.setHeader("Access-Control-Allow-Origin", "*");
        res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
        res.setHeader("Access-Control-Allow-Headers", "*");

        // Handle OPTIONS preflight request
        if (req.method === "OPTIONS") {
          res.statusCode = 200;
          res.end();
          return;
        }

        // Handle GET request
        if (req.method === "GET") {
          res.statusCode = 200;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify({ status: "ok" }));
          return;
        }

        next();
      });
    },
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), healthEndpointPlugin()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
  },
});
