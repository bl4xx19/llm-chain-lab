import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/admin": { target: "http://localhost:8000", changeOrigin: true },
      "/resolucion": { target: "http://localhost:8000", changeOrigin: true },
      "/chat": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
