// SikshaSetu student client — offline-first hub client + catalog.
export interface Asset { sha256: string; size: number; path: string; url?: string; tier: string; machine_generated?: boolean; reviewed?: boolean }
export interface Unit { id: string; course_slug: string; title: string; segments: {id: string; start: number; end: number; title: string; text: string}[]; assets: Record<string, Asset>; concepts: string[]; problems: string[] }
export interface Manifest { slug: string; meta: { title: string; term: string; license: string; attribution: Record<string, string> }; units: Unit[] }
export interface Concept { id: string; name: string; prerequisites: string[]; unit_refs: string[]; segment_refs: string[]; question_refs: string[] }
export interface Question { id: string; concept_ids: string[]; question: string; options: string[]; answer_index: number; reviewed: boolean; source: { unit_id: string; segment_id: string; timestamp: number } }
export interface Catalog { courses: { slug: string; title: string; term: string; ocw_url: string; license: string; attribution: Record<string, string> }[] }

export const HUB = location.origin;

let catalogCache: Catalog | null = null;
export async function fetchJSON<T>(url: string): Promise<T> {
  try {
    const r = await fetch(url, { cache: "no-store" });
    if (r.ok) return await r.json();
  } catch {
    // network or server down, fallback to bundled offline pack
  }
  try {
    const stripped = url.split("?")[0].replace(/^\/+/, "");
    const offlineUrl = url.startsWith("/offline-pack/") ? url : `/offline-pack/${stripped}`;
    const r2 = await fetch(offlineUrl);
    if (r2.ok) return await r2.json();
  } catch {
    // fallback failed
  }
  // Never throw to the UI
  if (url.includes("catalog")) return { courses: [] } as unknown as T;
  if (url.includes("concepts") || url.includes("questions")) return [] as unknown as T;
  return {} as unknown as T;
}
export async function getCatalog(): Promise<Catalog> { 
  catalogCache ??= await fetchJSON<Catalog>("/catalog.json"); 
  return catalogCache; 
}
export async function getConcepts(): Promise<Concept[]> { return fetchJSON<Concept[]>("/concepts.json"); }
export async function getQuestions(): Promise<Question[]> { return fetchJSON<Question[]>("/questions.json"); }
export async function getManifest(slug: string): Promise<Manifest> { return fetchJSON<Manifest>(`/${slug}.manifest.json`); }
export async function fetchAssetRange(sha: string, range?: [number, number]): Promise<Blob> {
  try {
    const r = await fetch(`/objects/${sha}`, range ? { headers: { Range: `bytes=${range[0]}-${range[1]}` } } : {});
    if (r.ok) return await r.blob();
  } catch {}
  try {
    const r2 = await fetch(`/offline-pack/sample/${sha}`);
    if (r2.ok) return await r2.blob();
  } catch {}
  return new Blob([]);
}
export async function searchOffline(q: string): Promise<{ query: string; matches: { type: string; id: string; name?: string; excerpt: string; ts?: number }[] }> {
  const [cat, con, qs, mans] = await Promise.all([getCatalog(), getConcepts(), getQuestions(),
    Promise.all([getManifest("6.006"), getManifest("6.100L"), getManifest("18.06")].map(p => p.catch(() => null as Manifest | null)))]);
  const out: { type: string; id: string; name?: string; excerpt: string; ts?: number }[] = [];
  const m = q.trim().toLowerCase();
  for (const c of (cat?.courses || [])) if (c.title?.toLowerCase().includes(m) || c.slug?.toLowerCase().includes(m))
    out.push({ type: "course", id: c.slug, excerpt: `${c.slug} · ${c.term || ""}` });
  for (const k of (con || [])) if (k.name?.toLowerCase().includes(m))
    out.push({ type: "concept", id: k.id, excerpt: `${k.name} · ${k.unit_refs?.join(", ") || ""}` });
  for (const u of (mans || []).filter(Boolean).flatMap(m => m!.units || []))
    for (const s of (u.segments || [])) {
      const hit = s.text?.toLowerCase().includes(m);
      if (hit) out.push({ type: "segment", id: s.id, name: u.title, excerpt: s.text.slice(0, 100) + "…", ts: s.start });
      if (out.length > 20) break;
    }
  for (const qu of (qs || [])) if (qu.question?.toLowerCase().includes(m) && out.length < 24)
    out.push({ type: "question", id: qu.id, excerpt: qu.question });
  return { query: q, matches: out.slice(0, 24) };
}
