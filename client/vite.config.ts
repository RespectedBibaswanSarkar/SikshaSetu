import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["icons/*.png"],
      manifest: {
        name: "SikshaSetu",
        short_name: "SikshaSetu",
        theme_color: "#0e1118",
        background_color: "#0e1118",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
        ],
      },
      workbox: {
        globDirectory: "dist",
        globPatterns: ["**/*.{js,css,html,svg,png,jpg,json,vtt,pdf,opus,mp4}"],
        runtimeCaching: [
          { urlPattern: /^https:\/\/.*\.hub\.lan|^\/objects\//, handler: "NetworkFirst",
            options: { cacheName: "ocw-content", networkTimeoutSeconds: 2 } },
        ],
      },
    }),
  ],
  server: { proxy: { "/api": "http://localhost:8000" } },
  test: { setupFiles: ["@testing-library/jest-dom/vitest"] },
});
