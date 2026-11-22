/**
 * store.ts — Single shared store using useSyncExternalStore.
 * Refetches /dashboard after every mutation so every screen updates instantly.
 */
import { useSyncExternalStore, useCallback } from "react";
import { api, Dashboard, HubError } from "./live";

export const SID_KEY = "sikshasetu_sid";

export function getSid(): string | null {
  return localStorage.getItem(SID_KEY);
}

export function setSid(sid: string) {
  localStorage.setItem(SID_KEY, sid);
}

export function clearSid() {
  localStorage.removeItem(SID_KEY);
}

// ── Dashboard store ──────────────────────────────────────────────────────

type StoreState =
  | { status: "loading" }
  | { status: "ok"; data: Dashboard }
  | { status: "error"; message: string }
  | { status: "onboarding" };

let state: StoreState = { status: "loading" };
const listeners = new Set<() => void>();

function notify() {
  listeners.forEach(l => l());
}

function setState(s: StoreState) {
  state = s;
  notify();
}

export function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => { listeners.delete(cb); };
}

export function getState(): StoreState {
  return state;
}

export async function fetchDashboard() {
  const sid = getSid();
  if (!sid) {
    setState({ status: "onboarding" });
    return;
  }
  setState({ status: "loading" });
  try {
    const data = await api.dashboard(sid);
    setState({ status: "ok", data });
  } catch (e) {
    if (e instanceof HubError) {
      setState({ status: "error", message: e.message });
    } else {
      setState({ status: "error", message: "Unknown error" });
    }
  }
}

// Initialize
(function init() {
  const sid = getSid();
  if (!sid) {
    state = { status: "onboarding" };
  } else {
    fetchDashboard();
  }
})();

// ── Hooks ────────────────────────────────────────────────────────────────

export function useStore() {
  return useSyncExternalStore(subscribe, getState);
}

export function useDashboard() {
  const s = useStore();
  const refetch = useCallback(() => fetchDashboard(), []);
  return { state: s, refetch };
}

/** Wrap any API mutation: call it, then refetch dashboard */
export async function mutate<T>(fn: () => Promise<T>): Promise<T> {
  const result = await fn();
  await fetchDashboard();
  return result;
}
