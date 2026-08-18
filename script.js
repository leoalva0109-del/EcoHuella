const currentPage = window.location.pathname.split("/").pop() || "index.html";
const navLinks = document.querySelectorAll(".top-nav a");
const navToggle = document.querySelector(".nav-toggle");
const themeToggle = document.querySelector(".theme-toggle");

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
  if (link.getAttribute("href") === currentPage) {
    link.classList.add("active");
  }

  link.addEventListener("click", () => {
    document.body.classList.remove("nav-open");
    navToggle?.setAttribute("aria-expanded", "false");
  });
});

navToggle?.addEventListener("click", () => {
  const isOpen = document.body.classList.toggle("nav-open");
  navToggle.setAttribute("aria-expanded", String(isOpen));
});

themeToggle?.addEventListener("click", () => {
  applyTheme(!document.body.classList.contains("dark-mode"));
});

document.querySelectorAll(".zoomable").forEach((img) => {
  img.addEventListener("click", () => {
    img.classList.toggle("active");
  });
});

const activateTabGroup = (buttons, panels, targetId, datasetKey, updateHash = false) => {
  const activeButton = Array.from(buttons).find((button) => button.dataset[datasetKey] === targetId);
  const activePanel = document.getElementById(targetId);

  if (!activeButton || !activePanel) {
    return false;
  }

  buttons.forEach((button) => {
    const isActive = button === activeButton;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });

  panels.forEach((panel) => {
    panel.hidden = panel.id !== targetId;
  });

  if (updateHash) {
    history.pushState(null, "", `#${targetId}`);
  }

  return true;
};

const phaseButtons = document.querySelectorAll("[data-tab-target]");
const phasePanels = document.querySelectorAll("[data-tab-panel]");
const subtabButtons = document.querySelectorAll("[data-subtab-target]");
const subtabPanels = document.querySelectorAll("[data-subtab-panel]");

const syncTabsFromHash = () => {
  const targetId = decodeURIComponent(window.location.hash.replace("#", ""));

  if (!targetId || !phaseButtons.length) {
    return;
  }

  const isSubtabTarget = Array.from(subtabButtons).some((button) => button.dataset.subtabTarget === targetId);

  if (isSubtabTarget) {
    activateTabGroup(phaseButtons, phasePanels, "fase-2", "tabTarget");
    activateTabGroup(subtabButtons, subtabPanels, targetId, "subtabTarget");
    requestAnimationFrame(() => document.getElementById("fase-2")?.scrollIntoView({ block: "start" }));
    return;
  }

  if (activateTabGroup(phaseButtons, phasePanels, targetId, "tabTarget")) {
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
    activateTabGroup(phaseButtons, phasePanels, "fase-2", "tabTarget");
    activateTabGroup(subtabButtons, subtabPanels, button.dataset.subtabTarget, "subtabTarget", true);
  });
});

syncTabsFromHash();
window.addEventListener("popstate", syncTabsFromHash);
