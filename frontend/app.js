// app.js
// Connects the frontend to the Flask backend running at API_BASE.
// If you deploy the backend elsewhere, just change API_BASE below.

const API_BASE = "http://127.0.0.1:5000/api";

let selectedSkills = new Set();
let selectedInterests = new Set();
let authMode = "login"; // or "signup"
let currentToken = localStorage.getItem("cpp_token") || null;
let currentUserName = localStorage.getItem("cpp_name") || null;

/* ============================================================
   Boot: check server + load skill/interest lists from backend
============================================================ */
window.addEventListener("DOMContentLoaded", async () => {
  updateAuthUI();
  await checkServer();
  await loadSkillsAndInterests();
});

async function checkServer() {
  const statusEl = document.getElementById("serverStatus");
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    if (data.status === "ok" && data.model_loaded) {
      statusEl.textContent = "● Backend server connected — ML model ready";
      statusEl.style.color = "var(--teal)";
    } else {
      statusEl.textContent = "⚠ Server is running but the model failed to load.";
      statusEl.style.color = "var(--danger)";
    }
  } catch (e) {
    statusEl.textContent = "⚠ Could not connect to the backend server. Start backend/app.py first (see README).";
    statusEl.style.color = "var(--danger)";
  }
}

async function loadSkillsAndInterests() {
  try {
    const res = await fetch(`${API_BASE}/skills`);
    const data = await res.json();
    buildChips("skillBox", data.skills, selectedSkills, "skillCount", "skills");
    buildChips("interestBox", data.interests, selectedInterests, "interestCount", "interest");
  } catch (e) {
    document.getElementById("skillBox").innerHTML =
      `<span class="hint" style="color:var(--danger)">Could not load skills from the server. Make sure the backend is running.</span>`;
  }
}

/* ============================================================
   Chip UI
============================================================ */
function buildChips(containerId, list, targetSet, countId, countLabel) {
  const box = document.getElementById(containerId);
  box.innerHTML = "";
  list.forEach((item) => {
    const chip = document.createElement("div");
    chip.className = "chip sans";
    chip.textContent = item;
    chip.onclick = () => {
      if (targetSet.has(item)) {
        targetSet.delete(item);
        chip.classList.remove("on");
      } else {
        targetSet.add(item);
        chip.classList.add("on");
      }
      document.getElementById(countId).textContent = `${targetSet.size} ${countLabel} selected`;
    };
    box.appendChild(chip);
  });
}

/* ============================================================
   Prediction
============================================================ */
async function predictCareers() {
  const warn = document.getElementById("formWarning");
  if (selectedSkills.size === 0) {
    warn.textContent = "Please select at least one skill.";
    return;
  }
  warn.textContent = "";

  const btn = document.getElementById("predictBtn");
  btn.disabled = true;
  btn.textContent = "Predicting...";

  try {
    const headers = { "Content-Type": "application/json" };
    if (currentToken) headers["Authorization"] = `Bearer ${currentToken}`;

    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        skills: Array.from(selectedSkills),
        interests: Array.from(selectedInterests),
      }),
    });
    let data = {};
    try { data = await res.json(); } catch (e) { /* the server sent a page that is not JSON */ }

    if (!res.ok) {
      warn.textContent = data.error || "Something went wrong on the server. Please try again.";
      return;
    }

    renderResults(data.results, data.prediction_id);
    document.getElementById("results").style.display = "block";
    scrollToId("results");
  } catch (e) {
    warn.textContent = "Could not connect to the server. Make sure the backend is running.";
  } finally {
    btn.disabled = false;
    btn.textContent = "Predict My Career";
  }
}

function renderResults(results, predictionId) {
  const wrap = document.getElementById("resultCards");
  wrap.innerHTML = "";

  results.forEach((r, idx) => {
    const card = document.createElement("div");
    card.className = "career-card" + (idx === 0 ? " top" : "");

    const haveTags = r.have_skills.length
      ? r.have_skills.map((s) => `<span class="tag have">${s}</span>`).join("")
      : `<span class="tag none">No matches yet</span>`;

    const needTags = r.missing_skills.length
      ? r.missing_skills.map((s) => `<span class="tag need">${s}</span>`).join("")
      : `<span class="tag none">Nothing missing — you're ready!</span>`;

    card.innerHTML = `
      <div class="career-card-head">
        <div>
          <h3>${idx === 0 ? "🏆 " : ""}${r.career}</h3>
          <p class="desc">${r.description}</p>
        </div>
        <div class="match-badge">
          <div class="num">${r.confidence}%</div>
          <div class="lbl">Match</div>
        </div>
      </div>
      <div class="gap-grid">
        <div class="gap-col have">
          <h4>Skills You Already Have</h4>
          <div class="tag-list">${haveTags}</div>
        </div>
        <div class="gap-col need">
          <h4>What You Still Need to Learn</h4>
          <div class="tag-list">${needTags}</div>
        </div>
      </div>
      <div class="resources"><b>How to learn:</b> ${r.resources}</div>
      <div class="feedback-row">
        <span class="sans" style="font-size:0.8rem;color:var(--muted)">Was this suggestion helpful?</span>
        <button class="fbtn yes" data-career="${r.career}">👍 Relevant</button>
        <button class="fbtn no" data-career="${r.career}">👎 Irrelevant</button>
      </div>
    `;
    wrap.appendChild(card);

    card.querySelector(".fbtn.yes").onclick = (e) => giveFeedback(e.target, r.career, predictionId, true);
    card.querySelector(".fbtn.no").onclick = (e) => giveFeedback(e.target, r.career, predictionId, false);
  });
}

async function giveFeedback(btn, career, predictionId, isYes) {
  const row = btn.parentElement;
  row.querySelectorAll(".fbtn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");

  try {
    await fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prediction_id: predictionId, career, is_relevant: isYes }),
    });
  } catch (e) {
    // If saving feedback fails, don't break the UI — fail silently.
  }
}

function resetForm() {
  selectedSkills.clear();
  selectedInterests.clear();
  document.querySelectorAll(".chip").forEach((c) => c.classList.remove("on"));
  document.getElementById("skillCount").textContent = "0 skills selected";
  document.getElementById("interestCount").textContent = "0 interest selected";
  document.getElementById("results").style.display = "none";
  document.getElementById("formWarning").textContent = "";
}

/* ============================================================
   Auth (Signup / Login) — JWT based
============================================================ */
function openAuthModal(mode) {
  authMode = mode;
  document.getElementById("authOverlay").classList.add("show");
  document.getElementById("authError").textContent = "";
  syncAuthModeUI();
}
function closeAuthModal() {
  document.getElementById("authOverlay").classList.remove("show");
}
function toggleAuthMode() {
  authMode = authMode === "login" ? "signup" : "login";
  syncAuthModeUI();
}
function syncAuthModeUI() {
  const isLogin = authMode === "login";
  document.getElementById("authTitle").textContent = isLogin ? "Login" : "Sign Up";
  document.getElementById("nameField").style.display = isLogin ? "none" : "block";
  document.getElementById("authSubmitBtn").textContent = isLogin ? "Login" : "Sign Up";
  document.getElementById("authSwitchText").textContent = isLogin ? "Don't have an account?" : "Already have an account?";
  document.getElementById("authSwitchLink").textContent = isLogin ? "Sign Up" : "Login";
}

async function submitAuth() {
  const errEl = document.getElementById("authError");
  errEl.textContent = "";

  const email = document.getElementById("authEmail").value.trim();
  const password = document.getElementById("authPassword").value;
  const name = document.getElementById("authName").value.trim();

  const endpoint = authMode === "login" ? "login" : "signup";
  const body = authMode === "login" ? { email, password } : { name, email, password };

  try {
    const res = await fetch(`${API_BASE}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    let data = {};
    try { data = await res.json(); } catch (e) { /* the server sent a page that is not JSON */ }

    if (!res.ok) {
      errEl.textContent = data.error || "Something went wrong on the server. Please try again.";
      return;
    }

    currentToken = data.token;
    currentUserName = data.name;
    localStorage.setItem("cpp_token", currentToken);
    localStorage.setItem("cpp_name", currentUserName);

    closeAuthModal();
    updateAuthUI();
  } catch (e) {
    errEl.textContent = "Could not connect to the server.";
  }
}

function logout() {
  currentToken = null;
  currentUserName = null;
  localStorage.removeItem("cpp_token");
  localStorage.removeItem("cpp_name");
  updateAuthUI();
}

function updateAuthUI() {
  const loggedIn = !!currentToken;
  document.getElementById("loginNavBtn").style.display = loggedIn ? "none" : "inline";
  document.getElementById("signupNavBtn").style.display = loggedIn ? "none" : "inline";
  document.getElementById("logoutBtn").style.display = loggedIn ? "inline" : "none";
  const greet = document.getElementById("userGreeting");
  if (loggedIn) {
    greet.style.display = "inline";
    greet.textContent = `Hi, ${currentUserName}`;
  } else {
    greet.style.display = "none";
  }
}

function scrollToId(id) {
  document.getElementById(id).scrollIntoView({ behavior: "smooth", block: "start" });
}
