# SikshaSetu — Licensing & Attribution

## MIT OpenCourseWare material (OCW)
- **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA)
- **Source:** https://ocw.mit.edu/ (MIT OpenCourseWare)
- **Per-asset attribution:** every asset in `pipeline/store/objects/` carries
  `{course_slug, course_page_url, url_or_yt_id, license, date_accessed}` in its manifest and
  per-asset flags `machine_generated`, `reviewed`. Attribution is rendered in the UI (Library, Course Details).

## Machine-generated / third-party content
- Transcripts produced by faster-whisper are marked `machine_generated: true` — review via the
  admin review screen before student use; OCW-hosted captions are `machine_generated: false`.
- Questions drafted by the pipeline are `reviewed: false` by default; admins approve in the admin review screen.

## Fair-use note
- Some OCW videos may have moved to YouTube (video.mit.edu → www.youtube.com redirects, e.g. 6.006 Spring 2020).
  YouTube-hosted lecture videos are flagged as such in `seed_report.md`.
- This is a non-commercial study tool for students (the OCW license covers non-commercial use).

## MIT OCW conditions
- By-NC-SA: You must give appropriate credit, provide a link to the license, indicate if changes were made,
  and share any adaptations under the same license (non-commercially).
