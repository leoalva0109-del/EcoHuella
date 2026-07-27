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