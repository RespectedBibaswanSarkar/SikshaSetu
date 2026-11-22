import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Only include our own test files
    include: ['tests/**/*.test.{js,ts,jsx,tsx}'],
    // Exclude node_modules and any other unwanted directories
    exclude: ['node_modules', 'tests/playwright.spec.ts'],
    // Setup files for jest-dom matchers
    setupFiles: ['@testing-library/jest-dom/vitest'],
    environment: 'jsdom',
  },
});
