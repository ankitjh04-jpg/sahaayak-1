# Follow-up verification — 2026-09-08

Original testing agent: `/app/test_reports/iteration_1.json`.

- Original backend regression: 12/12 passed. TypeScript and production build passed.
- Select warning fixed by moving composite dynamic text into native option `label` attributes in advisory and expert review selectors. Browser verifies `option span` count 0 and no hydration warnings.
- Offline auto-sync is expected; the manual retry button is only for pending items. Added a persistent, dismissible per-owner sync confirmation and immediate history refresh after automatic sync.
- Browser verified text + PNG saved while offline, queue/attachment preserved through offline page reload, reconnect replay, refreshed history, and persistent confirmation. Mobile queue/reload/reconnect overflow checks empty.
- Expired OTP verified through the public API: dedicated QA challenge expired one second in the past, valid demo code rejected with HTTP 400. No other user's challenge modified.
- Browser media denial path verified with `NotAllowedError`: visible Permission denied feedback, no recording begins, Punjabi interface remains usable.
- Expert source selector and review form verified at 1920×800 and 390×844; no overflow.
- Sonner's mobile list container extended 16px outside viewport despite visible toast fitting. Added explicit constrained width and positioned above mobile navigation. Final recheck recorded separately in screenshots.
- WhatsApp status polling now stops after a network status-unavailable response rather than repeating error toasts indefinitely.

Tests use public demo providers. No live SMS, model inference, weather, Whisper, or WhatsApp delivery was asserted.