import { useEffect, useRef, useState } from "react";
import { getManifest } from "./api";
import * as storage from "./storage";

export default function Offline({ page, setPage, playerOnly = false }) {
  const [mans, setMans] = useState<Record<string, storage.Manifest>>({});
  const [cur, setCur] = useState<{ manifest: storage.Manifest; unit: storage.Unit } | null>(null);
  const [t, setT] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const vidRef = useRef<HTMLVideoElement>(null);
  const [bookmarks, setBookmarks] = useState<{ unit: string; t: number; label: string }[]>([]);
  const [qIndex, setQIndex] = useState(0);
  const [ans, setAns] = useState<number | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    (async () => {
      const ms: Record<string, storage.Manifest> = {};
      for (const slug of ["6.006", "6.100L", "18.06"]) { try { ms[slug] = await getManifest(slug); } catch {} }
      setMans(ms);
      setBookmarks((await storage.loadState()).bookmarks ?? []);
    })();
  }, []);

  const pick = (u: storage.Unit) => {
    setCur({ manifest: Object.values(mans).find(m => m.units.includes(u))!, unit: u });
    setVideoUrl(null); setQIndex(0); setAns(null);
  };
  const seg = cur?.unit.segments[0];
  useEffect(() => { if (vidRef.current && seg) { vidRef.current.src = `/objects/${cur!.unit.assets.video_360p.sha256}`; vidRef.current.play(); } }, [cur]);
  const fmt = (t: number) => `${Math.floor(t / 60)}:${String(Math.floor(t) % 60).padStart(2, "0")}`;
  const addBookmark = () => setBookmarks(bs => [...bs, { unit: cur!.unit.id, t: Math.round(t), label: seg?.title || "Bookmark" }]);
  const jumpToBookmark = (b: { t: number }) => { if (vidRef.current) vidRef.current.currentTime = b.t; };

  return (
    <div>
      <h1>{playerOnly ? "Player" : "Library & Practice"}</h1>
      {!cur && (
        <div className="grid courses">
          {Object.values(mans).flatMap(m => m.units.map(u => ({ m: m.slug, u }))).map(x => (
            <div key={x.u.id} className="course-card">
              <div><b>{x.m}</b><br />{x.u.title.replace(/^Lecture \d+:? /i, "")}</div>
              <span className="muted small">{x.u.segments.length} topic{x.u.segments.length > 1 ? "s" : ""} · free to study offline</span>
              <button className="btn primary" onClick={() => pick(x.u)}>Study {x.m}</button>
            </div>
          ))}
        </div>
      )}
      {cur && !playerOnly && (
        <div>
          <h2>{cur.unit.title}</h2>
          {seg && <video ref={vidRef} className="video" controls preload="metadata" />}
          {seg && <div className="transcript-scroll"><b>Transcript</b><div>{seg.text}</div></div>}
          <button className="btn" onClick={addBookmark}>Bookmark ({fmt(t)})</button>
          <ul className="timeline">{bookmarks.filter(b => b.unit === cur!.unit.id).map(b => <li key={b.t} onClick={() => jumpToBookmark(b)}>{b.label} · {fmt(b.t)}</li>)}</ul>
          <h3>In-unit practice</h3>
          <p>{cur.unit.segments[0]?.text.slice(0, 120) || "—"}</p>
          <button className="btn primary" onClick={() => setPage("diagnostic")}>Open Diagnostic</button>
        </div>
      )}
      <h3>Your Bookmarks</h3>
      <ul className="bookmarks">{bookmarks.slice(-10).map(b => <li key={`${b.unit}-${b.t}`}>{b.label} · {fmt(b.t)}</li>)}</ul>
    </div>
  );
}
