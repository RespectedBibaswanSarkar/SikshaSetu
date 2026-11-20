// SikshaSetu on-device storage: OPFS (preferred) + localStorage (IndexedDB unavailable in file:// mode).
export interface StoredMastery { [unitId: string]: number }
export interface StoredState {
  mastery: StoredMastery;           // unitId → Elo-style rating in [0,10]
  questionAcc: Record<string, { ok: number; total: number }>;
  dailyMinutes: Record<string, number>; // YYYY-MM-DD → minutes
  libraryPlanOnly: boolean;
  completedUnits: string[];
}
const KEY = "ss-state";
const OPFS_DIR = ["SikshaSetu", "state"];

let mem: StoredState | null = null;
let opfs: FileSystemDirectoryHandle | null | undefined;

async function opfsDir() {
  if (opfs !== undefined) return opfs;
  opfs = null;
  try {
    opfs = await (navigator.storage.getDirectory());
    for (const seg of OPFS_DIR) opfs = await opfs.getDirectoryHandle(seg, { create: true });
  } catch { opfs = null; }
  return opfs;
}

async function opfsGet(name: string): Promise<StoredState | null> {
  const dir = await opfsDir();
  if (!dir) return null;
  const f = await dir.getFileHandle(name).catch(() => null);
  if (!f) return null;
  const file = await f.getFile();
  return JSON.parse(await file.text());
}

async function opfsPut(name: string, state: StoredState) {
  const dir = await opfsDir();
  if (!dir) return;
  const f = await dir.getFileHandle(name, { create: true });
  const wr = await f.createWritable();
  await wr.write(new Blob([JSON.stringify(state, null, 1)]));
  await wr.close();
}

export function initialState(): StoredState {
  return { mastery: {}, questionAcc: {}, dailyMinutes: {}, libraryPlanOnly: true, completedUnits: [] };
}

export async function loadState(): Promise<StoredState> {
  if (mem) return mem;
  mem = await opfsGet(KEY);
  if (!mem) {
    const ls = localStorage.getItem(KEY);
    if (ls) { try { mem = JSON.parse(ls); } catch { mem = null; } }
  }
  if (!mem) mem = initialState();
  mem = { ...initialState(), ...mem };
  return mem;
}

export async function saveState(s: StoredState): Promise<void> {
  mem = s;
  await opfsPut(KEY, s).catch(() => localStorage.setItem(KEY, JSON.stringify(s)));
}

export function getMastery(s: StoredState, unitId: string): number {
  return s.mastery[unitId] ?? 0.5;
}
export function setMastery(s: StoredState, unitId: string, v: number): void {
  s.mastery[unitId] = Math.max(0, Math.min(10, v));
}
export function recordMastery(s: StoredState, unitId: string, ok: boolean): void {
  const cur = getMastery(s, unitId);
  const target = ok ? Math.min(10, cur + 1.0) : Math.max(0, cur - 0.5);
  setMastery(s, unitId, cur * 0.85 + target * 0.15);
  s.questionAcc[unitId] = s.questionAcc[unitId] || { ok: 0, total: 0 };
  s.questionAcc[unitId].ok += ok ? 1 : 0;
  s.questionAcc[unitId].total += 1;
}
export function accuracy(s: StoredState, unitId: string): number {
  const a = s.questionAcc[unitId];
  if (!a || !a.total) return 0.5;
  return a.ok / a.total;
}
export function addTime(s: StoredState, unitId: string, min: number) {
  const d = new Date().toISOString().slice(0, 10);
  s.dailyMinutes[d] = (s.dailyMinutes[d] || 0) + Math.round(min);
}
export function weeklyHours(s: StoredState): number {
  const weekStart = new Date(Date.now() - 7 * 86400_000);
  return Object.entries(s.dailyMinutes).reduce((a, [d, m]) => (new Date(d) >= weekStart ? a + m : a), 0) / 60;
}
export function forgetting(s: StoredState, unitId: string): number {
  // exponential decay since last mastery update (approximated by times used this week)
  const recent = Object.keys(s.questionAcc[unitId] || {}).length;
  return Math.min(1, recent * 0.05);
}
