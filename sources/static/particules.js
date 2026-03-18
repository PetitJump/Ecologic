(function () {
  const canvas = document.getElementById('particules');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const particules = Array.from({length: 28}, () => ({
    x:       Math.random() * canvas.width,
    y:       Math.random() * canvas.height,
    r:       Math.random() * 3 + 1,
    vx:      (Math.random() - 0.5) * 0.35,
    vy:      -Math.random() * 0.5 - 0.1,
    opacite: Math.random() * 0.5 + 0.15,
    phase:   Math.random() * Math.PI * 2,
    couleur: ['#2d4a2d','#4a7c4a','#8b6f47','#7ab87a'][Math.floor(Math.random() * 4)]
  }));

  function dessiner() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const t = Date.now() / 1000;
    particules.forEach(p => {
      p.x += p.vx + Math.sin(t * 0.4 + p.phase) * 0.25;
      p.y += p.vy;
      if (p.y < -10)                p.y = canvas.height + 10;
      if (p.y < -10)                p.x = Math.random() * canvas.width;
      if (p.x < -10)                p.x = canvas.width + 10;
      if (p.x > canvas.width + 10)  p.x = -10;
      ctx.save();
      ctx.globalAlpha = p.opacite;
      ctx.fillStyle   = p.couleur;
      ctx.beginPath();
      ctx.ellipse(p.x, p.y, p.r * 2.5, p.r, Math.sin(t * 0.3 + p.phase) * 0.4, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    });
    requestAnimationFrame(dessiner);
  }
  dessiner();
})();
