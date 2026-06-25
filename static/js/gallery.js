document.querySelectorAll(".gallery-card").forEach((card, index) => {
  card.style.animationDelay = `${index * 45}ms`;
  card.classList.add("animate-in");
});
