const PARTICLE_COLORS = ["#fff176", "#ff80ab", "#80deea", "#b388ff", "#69f0ae", "#ffd180"];

function $(id) {
  return document.getElementById(id);
}

function createParticles() {
  const container = $("particles");
  if (!container) return;
  for (let i = 0; i < 24; i += 1) {
    const dot = document.createElement("span");
    dot.className = "particle";
    const size = 4 + Math.random() * 8;
    dot.style.width = `${size}px`;
    dot.style.height = `${size}px`;
    dot.style.left = `${Math.random() * 100}%`;
    dot.style.background = PARTICLE_COLORS[i % PARTICLE_COLORS.length];
    dot.style.animationDuration = `${5 + Math.random() * 7}s`;
    dot.style.animationDelay = `${Math.random() * 5}s`;
    container.appendChild(dot);
  }
}

function typewriter(element, text, speed = 42) {
  if (!element || !text) return;
  element.textContent = "";
  element.classList.add("typing");
  let index = 0;

  const tick = () => {
    if (index >= text.length) {
      element.classList.remove("typing");
      return;
    }
    element.textContent += text[index];
    index += 1;
    setTimeout(tick, speed);
  };

  tick();
}

function showApp() {
  $("loading")?.classList.add("hidden");
  $("error")?.classList.add("hidden");
  $("app")?.classList.remove("hidden");
}

function showError(message) {
  $("loading")?.classList.add("hidden");
  $("app")?.classList.add("hidden");
  const error = $("error");
  if (!error) return;
  error.classList.remove("hidden");
  const text = error.querySelector("p");
  if (text) text.textContent = message || "加载失败，请刷新重试";
}

function renderBlessing(data) {
  const contentEl = $("blessing-content");
  if (!contentEl) {
    showError("页面结构异常，请刷新重试");
    return;
  }
  if (!data?.content) {
    showError("祝福内容为空，请刷新重试");
    return;
  }

  const greetingEl = $("greeting");
  const introEl = $("intro");

  if (greetingEl && data.greeting) greetingEl.textContent = data.greeting;
  if (introEl && data.intro) introEl.textContent = data.intro;

  contentEl.textContent = "";
  setTimeout(() => typewriter(contentEl, data.content), 400);
}

async function fetchBlessing() {
  const res = await fetch("/api/blessing/random", { cache: "no-store" });
  if (!res.ok) {
    const payload = await res.json().catch(() => ({}));
    throw new Error(payload.detail || "加载失败");
  }
  return res.json();
}

function restartMascotGif() {
  const img = $("mascot-gif");
  if (!img) return;
  const base = img.src.split("?")[0];
  img.src = `${base}?t=${Date.now()}`;
}

async function loadBlessing(showLoader = false) {
  const refreshBtn = $("refresh-btn");
  if (refreshBtn) refreshBtn.disabled = true;

  if (showLoader) {
    $("app")?.classList.add("hidden");
    $("loading")?.classList.remove("hidden");
  } else {
    restartMascotGif();
  }

  try {
    const data = await fetchBlessing();
    showApp();
    renderBlessing(data);
  } catch (err) {
    showError(err?.message || "加载失败，请刷新重试");
  } finally {
    if (refreshBtn) refreshBtn.disabled = false;
  }
}

function init() {
  createParticles();
  loadBlessing(true);
  $("refresh-btn")?.addEventListener("click", () => loadBlessing(false));
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
