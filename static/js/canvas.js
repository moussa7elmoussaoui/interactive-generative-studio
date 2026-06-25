const palettes = {
  aurora: ["#7c3aed", "#2563eb", "#ec4899", "#fb923c"],
  cyber: ["#0ea5e9", "#d946ef", "#22c55e", "#facc15"],
  sunset: ["#f43f5e", "#f97316", "#a855f7", "#3b82f6"],
  mono: ["#e2e8f0", "#94a3b8", "#64748b", "#334155"]
};

function setupHero() {
  const canvas = document.getElementById("heroCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const t = 34;
  function drawStaticHero() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < 30; i += 1) {
      const color = palettes.aurora[i % palettes.aurora.length];
      const x = 260 + Math.cos(t * 0.01 + i) * (40 + i * 4.2);
      const y = 210 + Math.sin(t * 0.012 + i * 1.4) * (28 + i * 2.5);
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(t * 0.005 + i);
      ctx.globalAlpha = 0.12 + (i % 5) * 0.035;
      ctx.fillStyle = color;
      ctx.strokeStyle = "#ffffff55";
      ctx.lineWidth = 1;
      if (i % 3 === 0) ctx.arc(0, 0, 18 + i * 0.7, 0, Math.PI * 2);
      else ctx.rect(-12 - i * 0.3, -12 - i * 0.3, 24 + i * 0.6, 24 + i * 0.6);
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }
  }
  drawStaticHero();
}

class GeometryEditor {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.shapes = [];
    this.selected = null;
    this.dragging = false;
    this.offset = { x: 0, y: 0 };
    this.bind();
    this.draw();
  }

  bind() {
    this.canvas.addEventListener("pointerdown", (event) => {
      const point = this.point(event);
      this.selected = this.hit(point.x, point.y);
      if (this.selected) {
        this.dragging = true;
        this.offset.x = point.x - this.selected.x;
        this.offset.y = point.y - this.selected.y;
      } else {
        this.shapes.push({ type: "circle", x: point.x, y: point.y, size: 70, rotation: 0, color: "#ec4899cc", stroke: "#ffffffaa" });
      }
      this.draw();
    });
    this.canvas.addEventListener("pointermove", (event) => {
      if (!this.dragging || !this.selected) return;
      const point = this.point(event);
      this.selected.x = point.x - this.offset.x;
      this.selected.y = point.y - this.offset.y;
      this.draw();
    });
    window.addEventListener("pointerup", () => { this.dragging = false; });
    window.addEventListener("keydown", (event) => {
      if ((event.key === "Delete" || event.key === "Backspace") && this.selected) {
        this.shapes = this.shapes.filter((shape) => shape !== this.selected);
        this.selected = null;
        this.draw();
      }
      if (event.key.toLowerCase() === "c" && this.selected) {
        this.selected.color = palettes.aurora[Math.floor(Math.random() * palettes.aurora.length)] + "cc";
        this.draw();
      }
      if (event.key.startsWith("Arrow") && this.selected) {
        const delta = 12;
        if (event.key === "ArrowLeft") this.selected.x -= delta;
        if (event.key === "ArrowRight") this.selected.x += delta;
        if (event.key === "ArrowUp") this.selected.y -= delta;
        if (event.key === "ArrowDown") this.selected.y += delta;
        this.draw();
      }
    });
  }

  point(event) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) * (this.canvas.width / rect.width),
      y: (event.clientY - rect.top) * (this.canvas.height / rect.height)
    };
  }

  hit(x, y) {
    return [...this.shapes].reverse().find((shape) => Math.hypot((shape.x || 0) - x, (shape.y || 0) - y) < (shape.size || 60) / 2);
  }

  setShapes(shapes) {
    this.shapes = shapes;
    this.selected = null;
    this.draw();
  }

  draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.fillStyle = "#070916";
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.shapes.forEach((shape) => this.drawShape(shape));
  }

  drawShape(shape) {
    const ctx = this.ctx;
    ctx.save();
    ctx.translate(shape.x, shape.y);
    ctx.rotate((shape.rotation || 0) * Math.PI / 180);
    ctx.fillStyle = shape.color;
    ctx.strokeStyle = shape.stroke || "#ffffff88";
    ctx.lineWidth = 2;
    const size = shape.size || 60;
    if (shape.type === "line") {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo((shape.x2 || shape.x) - shape.x, (shape.y2 || shape.y) - shape.y);
      ctx.stroke();
    } else if (shape.type === "square") {
      ctx.fillRect(-size / 2, -size / 2, size, size);
      ctx.strokeRect(-size / 2, -size / 2, size, size);
    } else if (shape.type === "triangle") {
      ctx.beginPath();
      ctx.moveTo(0, -size / 2);
      ctx.lineTo(size / 2, size / 2);
      ctx.lineTo(-size / 2, size / 2);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.arc(0, 0, size / 2, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }
    if (shape === this.selected) {
      ctx.strokeStyle = "#ffffff";
      ctx.setLineDash([8, 8]);
      ctx.strokeRect(-size / 2 - 8, -size / 2 - 8, size + 16, size + 16);
    }
    ctx.restore();
  }

  download() {
    return this.canvas.toDataURL("image/png");
  }
}

class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas?.getContext("2d");
    this.particles = [];
    this.running = false;
    this.frameRequest = null;
    this.lastFrame = 0;
    this.mouse = { x: 0, y: 0, active: false };
    if (canvas) this.bind();
  }

  bind() {
    this.canvas.addEventListener("pointermove", (event) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = (event.clientX - rect.left) * (this.canvas.width / rect.width);
      this.mouse.y = (event.clientY - rect.top) * (this.canvas.height / rect.height);
      this.mouse.active = true;
    });
    this.canvas.addEventListener("pointerleave", () => { this.mouse.active = false; });
  }

  reset() {
    const count = Number(document.getElementById("particleCount")?.value || 80);
    const colors = palettes.cyber;
    this.particles = Array.from({ length: count }, () => ({
      x: Math.random() * this.canvas.width,
      y: Math.random() * this.canvas.height,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
      color: colors[Math.floor(Math.random() * colors.length)]
    }));
  }

  start() {
    if (!this.canvas) return;
    if (this.running) return;
    this.reset();
    this.running = true;
    this.loop();
  }

  loop() {
    if (!this.running) return;
    if (document.hidden) {
      this.frameRequest = requestAnimationFrame(() => this.loop());
      return;
    }
    const now = performance.now();
    if (now - this.lastFrame < 33) {
      this.frameRequest = requestAnimationFrame(() => this.loop());
      return;
    }
    this.lastFrame = now;
    const speed = Number(document.getElementById("particleSpeed")?.value || 1.4);
    const gravity = Number(document.getElementById("particleGravity")?.value || 0);
    const trail = Number(document.getElementById("trailLength")?.value || 0.16);
    const mode = document.getElementById("particleMode")?.value || "repel";
    const ctx = this.ctx;
    ctx.fillStyle = `rgba(7, 9, 22, ${trail})`;
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    const grid = this.buildGrid(120);
    this.particles.forEach((p) => {
      if (this.mouse.active) {
        const dx = this.mouse.x - p.x;
        const dy = this.mouse.y - p.y;
        const dist = Math.max(24, Math.hypot(dx, dy));
        const force = (mode === "attract" ? 1 : -1) * 42 / (dist * dist);
        p.vx += dx * force;
        p.vy += dy * force;
      }
      p.vy += gravity;
      p.x += p.vx * speed;
      p.y += p.vy * speed;
      if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
      this.nearbyParticles(grid, p, 120).forEach((q) => {
        if (q === p || q.id < p.id) return;
        const d = Math.hypot(p.x - q.x, p.y - q.y);
        if (d < 115) {
          ctx.strokeStyle = `rgba(120, 170, 255, ${1 - d / 115})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(q.x, q.y);
          ctx.stroke();
        }
      });
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fill();
    });
    this.frameRequest = requestAnimationFrame(() => this.loop());
  }

  buildGrid(cellSize) {
    const grid = new Map();
    this.particles.forEach((particle, id) => {
      particle.id = id;
      const key = `${Math.floor(particle.x / cellSize)},${Math.floor(particle.y / cellSize)}`;
      if (!grid.has(key)) grid.set(key, []);
      grid.get(key).push(particle);
    });
    return grid;
  }

  nearbyParticles(grid, particle, cellSize) {
    const cx = Math.floor(particle.x / cellSize);
    const cy = Math.floor(particle.y / cellSize);
    const nearby = [];
    for (let x = cx - 1; x <= cx + 1; x += 1) {
      for (let y = cy - 1; y <= cy + 1; y += 1) {
        nearby.push(...(grid.get(`${x},${y}`) || []));
      }
    }
    return nearby;
  }
}

async function postForm(url, form) {
  const response = await fetch(url, { method: "POST", body: new FormData(form) });
  if (!response.ok) throw new Error("Request failed");
  return response.json();
}

setupHero();

const geometryCanvas = document.getElementById("geometryCanvas");
const editor = geometryCanvas ? new GeometryEditor(geometryCanvas) : null;
const randomForm = document.getElementById("randomForm");
if (randomForm && editor) {
  randomForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = await postForm("/generative/random", randomForm);
    editor.setShapes(data.shapes);
    document.getElementById("downloadGeometry").href = editor.download();
  });
  document.getElementById("resetGeometry").addEventListener("click", () => editor.setShapes([]));
  document.getElementById("downloadGeometry").addEventListener("click", (event) => {
    event.currentTarget.href = editor.download();
  });
  editor.setShapes([
    { type: "circle", x: 260, y: 260, size: 150, rotation: 0, color: "#7c3aedaa", stroke: "#ffffff88" },
    { type: "square", x: 520, y: 340, size: 190, rotation: 24, color: "#2563eb99", stroke: "#ffffff88" },
    { type: "triangle", x: 820, y: 280, size: 180, rotation: -18, color: "#ec489999", stroke: "#ffffff88" }
  ]);
}

const particleCanvas = document.getElementById("particleCanvas");
const particles = new ParticleSystem(particleCanvas);
document.getElementById("startParticles")?.addEventListener("click", () => particles.start());
document.getElementById("pauseParticles")?.addEventListener("click", () => { particles.running = false; });
document.getElementById("resumeParticles")?.addEventListener("click", () => { if (!particles.running) { particles.running = true; particles.loop(); } });
document.getElementById("resetParticles")?.addEventListener("click", () => particles.reset());
document.getElementById("particleForm")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  await postForm("/generative/particles", event.currentTarget);
  alert("Particle artwork saved to the gallery.");
});
if (particleCanvas) {
  particles.reset();
  particles.ctx.fillStyle = "#070916";
  particles.ctx.fillRect(0, 0, particleCanvas.width, particleCanvas.height);
  particles.particles.forEach((p) => {
    particles.ctx.fillStyle = p.color;
    particles.ctx.beginPath();
    particles.ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
    particles.ctx.fill();
  });
}

const fractalForm = document.getElementById("fractalForm");
if (fractalForm) {
  fractalForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = await postForm("/generative/fractal", fractalForm);
    const preview = document.getElementById("fractalPreview");
    const empty = document.getElementById("fractalEmpty");
    preview.src = data.url;
    preview.classList.remove("hidden");
    empty?.classList.add("hidden");
    document.getElementById("downloadFractal").href = `/download/${data.filename}`;
  });
}
