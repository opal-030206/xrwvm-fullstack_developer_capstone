import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Django serves the production build from /static/, so keep the base path and
// the emitted file names stable.  Fixed names mean server/djangoapp/templates/
// index.html can reference them without a manifest lookup.
export default defineConfig({
  plugins: [react()],
  base: "/static/",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    assetsDir: "assets",
    rollupOptions: {
      output: {
        entryFileNames: "assets/index.js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: (assetInfo) =>
          assetInfo.name && assetInfo.name.endsWith(".css")
            ? "assets/index.css"
            : "assets/[name][extname]",
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/djangoapp": "http://localhost:8000",
    },
  },
});
