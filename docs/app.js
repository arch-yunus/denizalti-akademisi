const DATA_URL = "./data/projects.json";

const state = {
  data: null,
  filters: {
    domain: "all",
    trl: "all",
    query: ""
  }
};

const bandLabels = {
  early: "Konsept",
  prototype: "Prototip",
  mature: "Olgun"
};

const els = {
  domainGrid: document.querySelector("#domainGrid"),
  projectList: document.querySelector("#projectList"),
  platformGrid: document.querySelector("#platformGrid"),
  trlBars: document.querySelector("#trlBars"),
  insightText: document.querySelector("#insightText"),
  statDomains: document.querySelector("#statDomains"),
  statProjects: document.querySelector("#statProjects"),
  statMature: document.querySelector("#statMature"),
  domainFilter: document.querySelector("#domainFilter"),
  trlFilter: document.querySelector("#trlFilter"),
  searchInput: document.querySelector("#searchInput")
};

async function loadData() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`Veri dosyası yüklenemedi: ${response.status}`);
  }
  return response.json();
}

function trlBand(trl) {
  if (trl <= 3) return "early";
  if (trl <= 6) return "prototype";
  return "mature";
}

function filteredProjects() {
  const query = state.filters.query.toLocaleLowerCase("tr");
  return state.data.projects.filter((project) => {
    const matchesDomain = state.filters.domain === "all" || project.domainId === state.filters.domain;
    const matchesTrl = state.filters.trl === "all" || trlBand(project.trl) === state.filters.trl;
    const haystack = `${project.name} ${project.status} ${project.summary}`.toLocaleLowerCase("tr");
    return matchesDomain && matchesTrl && haystack.includes(query);
  });
}

function renderStats() {
  const matureCount = state.data.projects.filter((project) => project.trl >= 7).length;
  els.statDomains.textContent = state.data.domains.length;
  els.statProjects.textContent = state.data.projects.length;
  els.statMature.textContent = matureCount;
}

function renderDomains() {
  const counts = new Map();
  state.data.projects.forEach((project) => {
    counts.set(project.domainId, (counts.get(project.domainId) || 0) + 1);
  });

  els.domainGrid.innerHTML = state.data.domains.map((domain) => `
    <article class="domain-card">
      <h3>${domain.icon} ${domain.name}</h3>
      <p>${domain.focus}</p>
      <div class="domain-meta">
        <span>${counts.get(domain.id) || 0} teknoloji</span>
        <a href="${domain.source}">Modül</a>
      </div>
    </article>
  `).join("");
}

function renderFilters() {
  els.domainFilter.insertAdjacentHTML("beforeend", state.data.domains.map((domain) => `
    <option value="${domain.id}">${domain.name}</option>
  `).join(""));
}

function renderProjects() {
  const projects = filteredProjects();
  els.projectList.innerHTML = projects.map((project) => {
    const domain = state.data.domains.find((item) => item.id === project.domainId);
    return `
      <article class="project-card">
        <div class="trl-badge">TRL ${project.trl}</div>
        <div>
          <h3>${project.name}</h3>
          <p>${project.summary}</p>
          <a href="${project.source}">${domain.name} kaynağı</a>
        </div>
        <span class="status-pill">${bandLabels[trlBand(project.trl)]} · ${project.status}</span>
      </article>
    `;
  }).join("") || `<p class="empty">Bu filtrelerle eşleşen proje bulunamadı.</p>`;
}

function renderTrlBars() {
  const projects = filteredProjects();
  const counts = {
    "TRL 1-3": projects.filter((project) => project.trl <= 3).length,
    "TRL 4-6": projects.filter((project) => project.trl >= 4 && project.trl <= 6).length,
    "TRL 7-9": projects.filter((project) => project.trl >= 7).length
  };
  const max = Math.max(1, ...Object.values(counts));

  els.trlBars.innerHTML = Object.entries(counts).map(([label, count]) => `
    <div class="bar-row">
      <span>${label}</span>
      <div class="bar-track"><div class="bar-fill" style="width: ${(count / max) * 100}%"></div></div>
      <strong>${count}</strong>
    </div>
  `).join("");

  const dominant = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  els.insightText.textContent = `${projects.length} kayıt içinde en yoğun bant ${dominant[0]}. Filtreleri değiştirerek teknoloji olgunluk odağını karşılaştırabilirsiniz.`;
}

function renderPlatforms() {
  els.platformGrid.innerHTML = state.data.platforms.map((platform, index) => `
    <article class="platform-card">
      <small>#${index + 1} · ${platform.country}</small>
      <h3>${platform.name}</h3>
      <p>${platform.tagline}</p>
      <a href="${platform.source}">Profili aç</a>
    </article>
  `).join("");
}

function renderAll() {
  renderStats();
  renderDomains();
  renderProjects();
  renderTrlBars();
  renderPlatforms();
}

function bindEvents() {
  els.domainFilter.addEventListener("change", (event) => {
    state.filters.domain = event.target.value;
    renderProjects();
    renderTrlBars();
  });

  els.trlFilter.addEventListener("change", (event) => {
    state.filters.trl = event.target.value;
    renderProjects();
    renderTrlBars();
  });

  els.searchInput.addEventListener("input", (event) => {
    state.filters.query = event.target.value.trim();
    renderProjects();
    renderTrlBars();
  });
}

loadData()
  .then((data) => {
    state.data = data;
    renderFilters();
    renderAll();
    bindEvents();
  })
  .catch((error) => {
    els.projectList.innerHTML = `<p class="empty">${error.message}</p>`;
  });
