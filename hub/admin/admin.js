// SikshaSetu Admin Panel — hub API client (compact).
async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error(`${r.status} ${path}`);
  return r.json();
}
const H = {headers: {"Content-Type": "application/json"}};

function esc(s){return String(s??'').replace(/[&<>"]/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}

async function stats() {
  const [s, courses, imports, logs] = await Promise.all([
    api("/api/admin/stats"), api("/api/admin/courses"), api("/api/admin/imports"), api("/api/admin/logs")]);
  document.querySelector("#app").innerHTML = `
   <h1>Dashboard</h1><div class="grid" id="stats"></div>
   <div class="card"><h2>System Logs</h2><table><tr><th>ID</th><th>Time</th><th>Level</th><th>Message</th></tr>
   ${logs.slice(0,30).map(l=>`<tr><td>${l.id}</td><td>${new Date(l.ts*1e3).toLocaleString()}</td><td>${l.level}</td><td class="muted">${esc(l.msg)}</td></tr>`).join("")}</table></div>
   ${imports.length ? `<div class="card"><h2>Import Jobs</h2><table><tr><th>ID</th><th>URL</th><th>Stage</th><th>Status</th><th>Log</th></tr>
   ${imports.map(j=>`<tr><td>${esc(j.id)}</td><td><a href="${esc(j.ocw_url)}" target="_blank">${esc(j.ocw_url)}</a></td><td>${esc(j.stage)}</td><td class="badge ${j.status==='done'?'ok':j.status==='importing'?'pend':'err'}">${esc(j.status)}</td><td class="muted">${esc(j.log||'')}</td></tr>`).join("")}</table></div>` : ""}`;
  const st = s;
  document.querySelector("#stats").innerHTML = [
    ["Courses", st.courses], ["Students", st.students], ["Total storage", `${(st.storage_bytes/1e6).toFixed(1)} MB`],
    ["Institutions", st.institutions.join(", ") || "—"],
  ].map(([k,v])=>`<div class="stat"><span class="label">${k}</span><span class="v">${v}</span></div>`).join("");
  if (imports.length) {
    const j = imports[0];
    const poll = () => api(`/api/admin/import/${j.id}/status`).then(s2=>{
      const tr = document.querySelector(`[data-jid="${j.id}"] td:nth-child(3), [data-jid="${j.id}"] td:nth-child(4)`);
      if (s2.stage) { tr[0].textContent = s2.stage; tr[1].textContent = s2.status; }
      if (s2.status === "done" || s2.status === "failed") setTimeout(refresh, 3000);
      else setTimeout(poll, 2000);
    });
    setTimeout(poll, 500);
  }
  bind();
}
async function refresh() { await stats(); }

async function mapCourse() {
  const el = document.querySelector("#app");
  const [catalog] = await Promise.all([api("/catalog.json")]);
  el.innerHTML = `<h1>Map a Course from MIT OCW</h1>
   <div class="row"><input id="url" placeholder="Paste OCW course URL" list="urllist"><datalist id="urllist">
   ${(catalog.courses||[]).map(c=>`<option value="${c.ocw_url}">`).join("")}</datalist>
   <button class="primary" id="go">Map Course</button></div>
   <div id="status"></div>`;
  document.querySelector("#go").onclick = async () => {
    const url = document.querySelector("#url").value.trim();
    if (!url) return alert("paste a course URL");
    const j = await api("/api/admin/import", {method:"POST", ...H, body: JSON.stringify({ocw_url: url})});
    document.querySelector("#status").innerHTML = `<div class="card">Job ${esc(j.id)} running — <a href="/admin/">refresh Dashboard</a></div>`;
  };
}
async function courseDetails() {
  const [mans, concepts, questions] = await Promise.all([api("/api/admin/library"), api("/api/admin/concepts"), api("/api/admin/questions")]);
  let html = "<h1>Course Details</h1><table><tr><th>Course</th><th>Units</th><th>Segments</th><th>Concepts</th><th>Tiers</th><th>Attribution</th></tr>";
  for (const m of mans.slice(0,50)) {
    const tot = Object.values(m.tiers||{}).reduce((a,b)=>a+b,0);
    const att = m.attribution;
    html += `<tr><td>${esc(m.course)}/${esc(m.unit.slice(2))}</td><td>${m.units}</td><td>${m.segments}</td><td>${m.concepts}</td>
     <td class="muted">${Object.entries(m.tiers).map(([t,s])=>`<span class="chip chip-info">${t}:${(s/1e6).toFixed(1)}M</span>`).join(" ")}</td>
     <td class="attribution">${esc(att.course_page)} — CC BY-NC-SA</td></tr>`;
  }
  html += `</table><h2>Review Questions (${questions.length})</h2><table><tr><th>Status</th><th>Q</th><th>Concept</th></tr>`;
  for (const q of questions.slice(0,30)) html += `<tr><td class="badge ${q.reviewed?'ok':'pend'}">${q.reviewed?'approved':'pending'}</td><td class="muted">${esc(q.question)}</td><td>${(q.concept_ids||[]).map(esc).join(",")}</td></tr>`;
  html += "</table>";
  document.querySelector("#app").innerHTML = html;
}
async function systemLogs() {
  const logs = await api("/api/admin/logs");
  document.querySelector("#app").innerHTML = `<h1>System Logs</h1><table><tr><th>ID</th><th>Time</th><th>Level</th><th>Message</th></tr>
  ${logs.slice(0,200).map(l=>`<tr><td>${l.id}</td><td>${new Date(l.ts*1e3).toLocaleString()}</td><td>${esc(l.level)}</td><td class="muted">${esc(l.msg)}</td></tr>`).join("")}</table>`;
}
async function roster() {
  const db = await api("/api/admin/sync/export");
  document.querySelector("#app").innerHTML = `<h1>Student Roster</h1><table><tr><th>ID</th><th>Name</th><th>Cohort</th><th>Sync Code</th><th>Masteries</th></tr>
  ${db.slice(0,50).map(s=>`<tr><td>${esc(s.id)}</td><td>${esc(s.name||'—')}</td><td>${esc(s.cohort||'—')}</td><td class="muted">${esc(s.progress_code||'—')}</td><td class="muted">${esc(s.masteries||'')}</td></tr>`).join("")}</table>`;
}
function bind() {
  const t = location.hash;
  document.querySelectorAll("nav button").forEach((b,i)=>b.onclick = () => { location.hash = `#${i+1}`; show(); });
  const n = Number(t.replace("#","")) || 1;
  document.querySelectorAll("nav button")[n-1].click();
}
let shown = false;
async function show() {
  if (!shown) { document.querySelector("h1")?.remove(); shown = true; }
  const tab = Number(location.hash.replace("#","")) || 1;
  const f = [stats, mapCourse, courseDetails, systemLogs, roster, roster][tab-1];
  await f();
}
document.addEventListener("DOMContentLoaded", () => { show(); });
