# SikshaSetu Data Schema (docs/schema.md)

Single source of truth for all data shapes. Everything conforms to it.

## Course
```json
{
  "slug": "6.006",                      // stable id, e.g. "6.006"
  "number": "6.006",
  "title": "Introduction to Algorithms",
  "institution": "MIT",
  "term": "Spring 2020",
  "ocw_url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
  "license": "CC-BY-NC-SA-4.0",
  "attribution": { "course_page": "https://ocw.mit.edu/...", "page_sha256": "...", "page_size": 123, "date_accessed": "2026-11-20" }
}
```

## Unit (lecture)
```json
{
  "id": "6.006/u03",
  "course_slug": "6.006",
  "index": 3,
  "title": "Dynamic Programming",
  "ocw_url": "https://ocw.mit.edu/courses/.../...",
  "duration_min": 50,
  "assets": {
    "video_360p":    { "sha256": "...", "size": 123456, "tier": "video_360p", "url": "...", "machine_generated": false, "reviewed": false },
    "audio_only":    { "sha256": "...", "size": ...,     "tier": "audio_only",  "url": "...", "machine_generated": false, "reviewed": false },
    "notes_pdf":     { "sha256": "...", "size": ...,     "tier": "notes_pdf",   "url": "...", "machine_generated": false, "reviewed": false },
    "transcript_vtt":{ "sha256": "...", "size": ...,     "tier": "transcript_vtt", "url": "...", "machine_generated": false, "reviewed": true },
    "problem_set":   { "sha256": "...", "size": ...,     "tier": "problem_set", "url": "...", "machine_generated": false, "reviewed": true },
    "solutions":     { "sha256": "...", "size": ...,     "tier": "solutions",   "url": "...", "machine_generated": false, "reviewed": true },
    "poster":        { "sha256": "...", "size": ...,     "tier": "poster",      "url": "...", "machine_generated": true,  "reviewed": false }
  },
  "segments": [ { "id": "6.006/u03/s1", "start": 120.0, "end": 480.0, "title": "Recurrence & memoization", "text": "...", "unit_id": "6.006/u03" } ],
  "concepts": [ "concept_id", ... ],
  "problems":  [ "problem_id", ... ]
}
```

## Concept (concepts.json)
```json
{ "id": "6.006/c-dynamic_programming", "name": "Dynamic programming",
  "prerequisites": ["6.006/c-recursion", "6.006/c-recurrence"],
  "unit_refs": ["6.006/u03"], "segment_refs": ["6.006/u03/s1"],
  "question_refs": ["6.006/q1", "6.006/q2"] }
```

## Question (questions.json) — has `reviewed` flag
```json
{ "id": "6.006/q1", "concept_ids": ["6.006/c-dynamic_programming"],
  "question": "What technique solves problems by combining answers to overlapping subproblems?",
  "options": ["Dynamic programming", "BFS", "Greedy choice", "Topological sort"],
  "answer_index": 0, "difficulty": 1,
  "source": { "unit_id": "6.006/u03", "segment_id": "6.006/u03/s1", "timestamp": 240.0 },
  "reviewed": false }
```

## Content store (hub/content/objects/<sha256>)
Content-addressed object store. Plus at store root:
- `catalog.json` — { courses: [...], version }
- `concepts.json` — all concepts across courses
- `questions.json` — all questions (with `reviewed` flag)
- `version.json` — { content_version, generated_at, seed_report }
- `<slug>.manifest.json` — per-course manifest (units + assets map + attribution)

## Per-student manifest (generated on-device)
From catalog + on-device mastery + storage budget: `{ courses, units_included[], storage_bytes, budget_bytes }`.

## Sync codes (progress export)
Base32-ish encoding of on-device mastery vector: `SS-<checksum>-<b64>` format for QR/paste sync with admin.
