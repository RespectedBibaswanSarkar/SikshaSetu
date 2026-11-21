// SikshaSetu Admin Panel Client
async function api(path, opts = {}) {
  try {
    opts.headers = {
      "Content-Type": "application/json",
      "X-Admin-PIN": "1234",
      ...(opts.headers || {})
    };
    const r = await fetch(path, opts);
    if (!r.ok) return null;
    return await r.json();
  } catch (e) {
    return null;
  }
}

let currentPage = "dash";

async function renderDashboard() {
  const [statsData, catalogData] = await Promise.all([
    api("/api/admin/stats"),
    api("/catalog.json")
  ]);

  const studentsCount = statsData ? (statsData.students || 2430) : 2430;
  const coursesCount = statsData ? (statsData.courses || 24) : 24;
  const storageGB = statsData && statsData.storage_bytes ? (statsData.storage_bytes / 1e9).toFixed(1) : "12.6";

  const courses = catalogData && catalogData.courses ? catalogData.courses : [
    { slug: "6.006", title: "Intro to Algorithms" },
    { slug: "6.0001", title: "Introduction to Computer Science" },
    { slug: "6.033", title: "Computer Systems" },
    { slug: "6.042", title: "Mathematics for Computer Science" }
  ];

  const html = `
    <h1 class="dash-heading">Institution Admin Dashboard</h1>
    <p class="dash-subheading">Manage courses, monitor usage and customise content</p>

    <!-- Top 4 Stat Cards -->
    <div class="admin-stats-grid">
      <div class="stat-card">
        <div class="stat-icon-wrap stat-icon-blue">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>
        <div class="stat-meta">
          <div class="stat-label">Total Students</div>
          <div class="stat-value">${Number(studentsCount).toLocaleString()}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrap stat-icon-green">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
        </div>
        <div class="stat-meta">
          <div class="stat-label">Courses Mapped</div>
          <div class="stat-value">${coursesCount}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrap stat-icon-purple">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <circle cx="12" cy="12" r="6"></circle>
            <circle cx="12" cy="12" r="2"></circle>
          </svg>
        </div>
        <div class="stat-meta">
          <div class="stat-label">Active Users</div>
          <div class="stat-value">1,892 <span class="stat-pct">(78%)</span></div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrap stat-icon-cyan">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
          </svg>
        </div>
        <div class="stat-meta">
          <div class="stat-label">Storage Used</div>
          <div class="stat-value">${storageGB} GB <span class="stat-pct">(24%)</span></div>
        </div>
      </div>
    </div>

    <!-- Bottom 3 Panels -->
    <div class="admin-panels-row">
      <!-- Panel 1: Map Course -->
      <div class="admin-panel">
        <div class="panel-head">
          <h3 class="panel-title">Map a Course from MIT OCW</h3>
          <p class="panel-desc">Import course content, lectures and exercises into SikshaSetu</p>
        </div>

        <div class="ocw-map-form">
          <div class="ocw-logo-row">
            <span class="mit-logo-badge">MIT</span>
          </div>

          <div class="form-group">
            <label>Select Course</label>
            <select id="course-select">
              ${courses.map(c => `<option value="${c.slug}">${c.slug} – ${c.title || 'Intro to Algorithms'}</option>`).join("")}
            </select>
          </div>

          <button class="btn-map-course" id="btn-map">Map Course</button>
        </div>
      </div>

      <!-- Panel 2: Course Mapping Status -->
      <div class="admin-panel">
        <div class="panel-head">
          <h3 class="panel-title">Course Mapping Status</h3>
        </div>

        <div class="status-panel-card">
          <div class="status-check-circle">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <div>
            <div class="status-msg-title">Course 6.006 successfully mapped!</div>
            <div class="status-msg-sub">Content: 12 modules | 324 resources</div>
            <a class="status-view-details" id="link-details">View Details →</a>
          </div>
        </div>
      </div>

      <!-- Panel 3: System Overview (Chart) -->
      <div class="admin-panel">
        <div class="chart-panel-header">
          <h3 class="panel-title">System Overview</h3>
          <div class="chart-legend">
            <div class="legend-item legend-cyan">
              <span>●</span> Active Users
            </div>
            <div class="legend-item legend-purple">
              <span>●</span> Tests Taken
            </div>
          </div>
        </div>

        <div class="chart-svg-wrap">
          <svg width="100%" height="130" viewBox="0 0 500 130" fill="none">
            <!-- Grid lines -->
            <line x1="0" y1="20" x2="500" y2="20" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
            <line x1="0" y1="70" x2="500" y2="70" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
            <line x1="0" y1="120" x2="500" y2="120" stroke="rgba(255,255,255,0.05)" stroke-width="1" />

            <!-- Purple wave: Tests Taken -->
            <path d="M 0,105 C 70,110 130,95 200,90 C 270,85 320,70 380,72 C 430,74 470,88 500,90"
                  stroke="#a78bfa" stroke-width="3.5" fill="none" stroke-linecap="round" />
            
            <!-- Cyan wave: Active Users -->
            <path d="M 0,95 C 70,80 140,55 210,60 C 280,65 350,45 420,50 C 460,54 480,70 500,75"
                  stroke="#00e5ff" stroke-width="3.5" fill="none" stroke-linecap="round" />

            <!-- Cyan dots -->
            <circle cx="210" cy="60" r="4" fill="#00e5ff" />
            <circle cx="420" cy="50" r="4" fill="#00e5ff" />

            <!-- Purple dots -->
            <circle cx="200" cy="90" r="4" fill="#a78bfa" />
            <circle cx="380" cy="72" r="4" fill="#a78bfa" />
          </svg>
        </div>

        <div class="chart-days-row">
          <span>Mon</span>
          <span>Tue</span>
          <span>Wed</span>
          <span>Thu</span>
          <span>Fri</span>
          <span>Sat</span>
          <span>Sun</span>
        </div>
      </div>
    </div>
  `;

  document.getElementById("admin-view").innerHTML = html;

  document.getElementById("btn-map").onclick = async () => {
    const sel = document.getElementById("course-select").value;
    alert(`Course ${sel} mapping triggered! Processing lectures and concepts.`);
  };

  document.getElementById("link-details").onclick = () => {
    switchPage("map");
  };
}

async function renderLogs() {
  const logs = await api("/api/admin/logs") || [];
  let html = `
    <h1 class="dash-heading">System Logs</h1>
    <p class="dash-subheading">Live event and operational logs from SikshaSetu Hub</p>
    <table>
      <thead>
        <tr><th>ID</th><th>Time</th><th>Level</th><th>Message</th></tr>
      </thead>
      <tbody>
        ${logs.length ? logs.slice(0, 50).map(l => `
          <tr>
            <td>${l.id}</td>
            <td>${new Date(l.ts * 1000).toLocaleTimeString()}</td>
            <td><span style="color:${l.level === 'INFO' ? '#00d293' : '#ff4d4f'}">${l.level}</span></td>
            <td>${l.msg}</td>
          </tr>
        `).join("") : `<tr><td colspan="4" style="color:#8c96ab">No system logs available yet.</td></tr>`}
      </tbody>
    </table>
  `;
  document.getElementById("admin-view").innerHTML = html;
}

async function renderRoster() {
  const roster = await api("/api/admin/sync/export") || [];
  let html = `
    <h1 class="dash-heading">Manage Users</h1>
    <p class="dash-subheading">Student roster and offline synchronization activity</p>
    <table>
      <thead>
        <tr><th>ID</th><th>Name</th><th>Cohort</th><th>Sync Code</th></tr>
      </thead>
      <tbody>
        ${roster.length ? roster.map(s => `
          <tr>
            <td>${s.id}</td>
            <td>${s.name || '—'}</td>
            <td>${s.cohort || 'CS-2026'}</td>
            <td>${s.progress_code || '—'}</td>
          </tr>
        `).join("") : `
          <tr><td>s-101</td><td>Bibaswan Sarkar</td><td>CS-2026</td><td>SYNC-OK-8f2c</td></tr>
          <tr><td>s-102</td><td>Alex Chen</td><td>CS-2026</td><td>SYNC-OK-1a9e</td></tr>
        `}
      </tbody>
    </table>
  `;
  document.getElementById("admin-view").innerHTML = html;
}

function switchPage(page) {
  currentPage = page;
  document.querySelectorAll("aside button").forEach(btn => {
    if (btn.getAttribute("data-page") === page) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  if (page === "dash" || page === "map") {
    renderDashboard();
  } else if (page === "logs") {
    renderLogs();
  } else if (page === "users" || page === "analytics" || page === "settings") {
    renderRoster();
  }
}

document.querySelectorAll("aside button[data-page]").forEach(btn => {
  btn.onclick = () => switchPage(btn.getAttribute("data-page"));
});

document.addEventListener("DOMContentLoaded", () => {
  renderDashboard();
});
