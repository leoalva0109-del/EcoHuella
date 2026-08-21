const currentPage = window.location.pathname.split("/").pop() || "index.html";
const phaseOnePages = new Set([
  "fases.html",
  "ia.html",
  "tecnico.html",
  "materiales.html",
  "metodologia.html",
  "diagramas.html",
]);
const activePage = phaseOnePages.has(currentPage) ? "fases.html" : currentPage;
const siteHeader = document.querySelector(".site-header");
const navLinks = document.querySelectorAll(".top-nav a");
const navToggle = document.querySelector(".nav-toggle");
const themeToggle = document.querySelector(".theme-toggle");

const setNavOpen = (isOpen, returnFocus = false) => {
  document.body.classList.toggle("nav-open", isOpen);

  if (navToggle) {
    navToggle.setAttribute("aria-expanded", String(isOpen));
    navToggle.setAttribute("aria-label", isOpen ? "Cerrar navegación" : "Abrir navegación");
    if (!isOpen && returnFocus) navToggle.focus();
  }

};

const applyTheme = (isDark) => {
  document.body.classList.toggle("dark-mode", isDark);
  localStorage.setItem("ecohuella-theme", isDark ? "dark" : "light");
  if (themeToggle) {
    themeToggle.textContent = isDark ? "☀️ Claro" : "🌙 Oscuro";
    themeToggle.setAttribute("aria-pressed", String(isDark));
  }
};

const savedTheme = localStorage.getItem("ecohuella-theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(savedTheme ? savedTheme === "dark" : prefersDark);

navLinks.forEach((link) => {
  const linkPage = new URL(link.href, window.location.href).pathname.split("/").pop();
  if (linkPage === activePage) {
    link.classList.add("active");
    link.setAttribute("aria-current", "page");
  }

  link.addEventListener("click", () => setNavOpen(false));
});

navToggle?.addEventListener("click", () => {
  setNavOpen(!document.body.classList.contains("nav-open"));
});

themeToggle?.addEventListener("click", () => {
  applyTheme(!document.body.classList.contains("dark-mode"));
});

document.addEventListener("click", (event) => {
  if (document.body.classList.contains("nav-open") && siteHeader && !siteHeader.contains(event.target)) {
    setNavOpen(false);
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && document.body.classList.contains("nav-open")) {
    event.preventDefault();
    setNavOpen(false, true);
    return;
  }

});

window.addEventListener("resize", () => {
  if (window.innerWidth > 1024) setNavOpen(false);
});

document.querySelectorAll(".zoomable").forEach((img) => {
  img.addEventListener("click", () => img.classList.toggle("active"));
});

const activateTabGroup = (buttons, panels, targetId, datasetKey, updateHash = false) => {
  const activeButton = Array.from(buttons).find((button) => button.dataset[datasetKey] === targetId);
  const activePanel = document.getElementById(targetId);

  if (!activeButton || !activePanel) return false;

  buttons.forEach((button) => {
    const isActive = button === activeButton;
    button.classList.toggle("active", isActive);
    if (button.getAttribute("role") === "tab") {
      button.setAttribute("aria-selected", String(isActive));
      button.tabIndex = isActive ? 0 : -1;
    }
  });

  panels.forEach((panel) => {
    panel.hidden = panel.id !== targetId;
  });

  if (updateHash) history.pushState(null, "", `#${targetId}`);
  return true;
};

const phaseButtons = document.querySelectorAll("[data-tab-target]");
const phasePanels = document.querySelectorAll("[data-tab-panel]");
const subtabButtons = document.querySelectorAll("[data-subtab-target]");
const subtabPanels = document.querySelectorAll("[data-subtab-panel]");

const syncTabsFromHash = () => {
  const targetId = decodeURIComponent(window.location.hash.replace("#", ""));
  if (!targetId) return;

  const targetElement = document.getElementById(targetId);
  const containingSubtab = targetElement?.closest("[data-subtab-panel]");

  if (containingSubtab) {
    if (phaseButtons.length) activateTabGroup(phaseButtons, phasePanels, "fase-2", "tabTarget");
    activateTabGroup(subtabButtons, subtabPanels, containingSubtab.id, "subtabTarget");
    requestAnimationFrame(() => targetElement.scrollIntoView({ block: "start" }));
    return;
  }

  if (phaseButtons.length && activateTabGroup(phaseButtons, phasePanels, targetId, "tabTarget")) {
    requestAnimationFrame(() => document.getElementById(targetId)?.scrollIntoView({ block: "start" }));
  }
};

phaseButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activateTabGroup(phaseButtons, phasePanels, button.dataset.tabTarget, "tabTarget", true);
  });
});

subtabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (phaseButtons.length) activateTabGroup(phaseButtons, phasePanels, "fase-2", "tabTarget");
    activateTabGroup(subtabButtons, subtabPanels, button.dataset.subtabTarget, "subtabTarget", true);
  });
});

const bindTabKeyboard = (buttons) => {
  const list = Array.from(buttons);
  list.forEach((button, index) => {
    button.addEventListener("keydown", (event) => {
      let nextIndex = null;
      if (event.key === "ArrowRight") nextIndex = (index + 1) % list.length;
      if (event.key === "ArrowLeft") nextIndex = (index - 1 + list.length) % list.length;
      if (event.key === "Home") nextIndex = 0;
      if (event.key === "End") nextIndex = list.length - 1;
      if (nextIndex === null) return;

      event.preventDefault();
      list[nextIndex].focus();
      list[nextIndex].click();
    });
  });
};

bindTabKeyboard(document.querySelectorAll('.phase-section-tabs [role="tab"]'));
syncTabsFromHash();
window.addEventListener("popstate", syncTabsFromHash);
window.addEventListener("hashchange", syncTabsFromHash);
