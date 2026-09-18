import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// `globals` is intentionally off in vite.config.ts (tests import from
// 'vitest' explicitly), so @testing-library/react's own auto-cleanup never
// triggers — without this, DOM from one test leaks into the next.
afterEach(() => {
  cleanup()
})
