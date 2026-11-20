# SikshaSetu Demo — 5-Minute Offline-First Demo Script

## Setup (host)
1. `make seed` — resolves + fetches lecture videos from MIT OCW YouTube (rate-limited) + notes/transcripts.
2. `make serve-lan` — prints the Hub URL (e.g. `http://192.168.1.20:8000`) + a QR code.

## The 5 minutes
1. **Hub on LAN:** `make serve-lan` — phone/laptop on the same Wi-Fi sees the Hub (admin at `/admin/`).
2. **Student PWA:** open the Hub on a phone; install the SikshaSetu PWA (or open `/` on laptop).
3. **Download a course:** student downloads the course from the Library tab (video + transcript + notes).
4. **Airplane mode:** enable airplane mode on the device — verify everything works.
5. **Diagnostic:** student runs the adaptive diagnostic (8–12 questions over the prerequisite graph).
6. **Personalised plan:** student opens the Dashboard — the bandit-backed recommender picks the next unit.
7. **Mock test:** student runs the weekly mock test (timed, auto-graded).
8. **Weak-point report:** Dashboard shows the top-3 weak points + pacing recommendations.
9. **Admin import:** open `/admin/` (top bar "SikshaSetu – Admin Panel"), click "Map a Course", paste a new MIT OCW course URL — live stage progress + gap report.

## Notes
- No central student database: progress is on-device (OPFS); sync via progress codes or admin roster import.
- License: OCW material is CC BY-NC-SA (see `docs/LICENSES.md`); machine-generated transcripts flagged.
- If Tauri/Android toolchains are missing: `cargo install cargo-generate` etc. — see README "Install".
