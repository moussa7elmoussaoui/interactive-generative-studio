const nav = document.querySelector(".nav");
const navToggle = document.querySelector(".nav-toggle");
if (navToggle) {
  navToggle.addEventListener("click", () => nav.classList.toggle("open"));
}

document.querySelectorAll("[data-count]").forEach((element) => {
  const target = Number(element.dataset.count || 0);
  let current = 0;
  const step = Math.max(1, Math.ceil(target / 42));
  const timer = setInterval(() => {
    current = Math.min(target, current + step);
    element.textContent = current;
    if (current >= target) clearInterval(timer);
  }, 24);
});
