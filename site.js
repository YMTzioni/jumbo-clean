// ג׳מבו קלין v5, L2 interactions (DESIGN.md §7). Motion ideas after vue-bits by DavidHDev (MIT).
(() => {
  const doc = document.documentElement;
  doc.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

  // SplitText / ScrollReveal: wrap words of [data-split] and .lead[data-words]
  const wrapWords = (root) => {
    let i = 0;
    const walk = (node) => {
      [...node.childNodes].forEach((n) => {
        if (n.nodeType === 3) {
          const parts = n.textContent.split(/(\s+)/);
          const frag = document.createDocumentFragment();
          parts.forEach((p) => {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
            const s = document.createElement('span');
            s.className = 'w'; s.style.setProperty('--i', i++); s.textContent = p;
            frag.appendChild(s);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') walk(n);
      });
    };
    walk(root);
  };
  document.querySelectorAll('[data-split],.lead[data-words]').forEach(wrapWords);

  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -10% 0px' });
  document.querySelectorAll('[data-split],[data-reveal],.lead[data-words]').forEach((el) => io.observe(el));
  // hero headline starts at once
  requestAnimationFrame(() => document.querySelectorAll('.hero [data-split],.s-hero [data-split],.hero .lead,.s-hero .lead').forEach((el) => el.classList.add('in')));

  // nav scrolled state
  const nav = document.querySelector('.nav');
  const onScroll = () => nav && nav.classList.toggle('scrolled', scrollY > 24);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // close mega menu on outside click / Escape
  const mega = document.querySelector('.nav details');
  if (mega) {
    document.addEventListener('click', (e) => { if (!mega.contains(e.target)) mega.open = false; });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') mega.open = false; });
  }

  // mobile sheet
  const sheet = document.getElementById('sheet');
  document.querySelectorAll('[data-sheet]').forEach((b) => b.addEventListener('click', () => {
    const open = !sheet.classList.contains('open');
    sheet.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    document.querySelector('.nav-menu').setAttribute('aria-expanded', open);
  }));
  sheet && sheet.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => { sheet.classList.remove('open'); document.body.style.overflow = ''; }));

  // SpotlightCard: pointer position into --mx/--my (rAF throttled)
  if (fine) document.querySelectorAll('.card').forEach((c) => {
    let raf = 0;
    c.addEventListener('pointermove', (e) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const r = c.getBoundingClientRect();
        c.style.setProperty('--mx', `${e.clientX - r.left}px`);
        c.style.setProperty('--my', `${e.clientY - r.top}px`);
        raf = 0;
      });
    });
  });

  // Magnet CTA
  if (fine && !reduce) document.querySelectorAll('[data-magnet]').forEach((b) => {
    let raf = 0;
    b.addEventListener('pointermove', (e) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const r = b.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) * 0.22;
        const y = (e.clientY - r.top - r.height / 2) * 0.32;
        b.style.translate = `${x}px ${y}px`;
        raf = 0;
      });
    });
    b.addEventListener('pointerleave', () => { b.style.translate = ''; });
  });

  // ClickSpark with the logo's four-point sparkle
  const SPARK = 'M9 0Q9 9 18 9Q9 9 9 18Q9 9 0 9Q9 9 9 0Z';
  const burst = (x, y, n = 7, dist = 46) => {
    if (reduce) return;
    for (let k = 0; k < n; k++) {
      const a = (Math.PI * 2 * k) / n + Math.random() * 0.4;
      const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      s.setAttribute('viewBox', '0 0 18 18'); s.setAttribute('class', 'spark-fx'); s.setAttribute('aria-hidden', 'true');
      s.innerHTML = `<path d="${SPARK}"/>`;
      s.style.left = `${x}px`; s.style.top = `${y}px`;
      const d = dist * (0.7 + Math.random() * 0.6);
      s.style.setProperty('--dx', `${Math.cos(a) * d}px`); s.style.setProperty('--dy', `${Math.sin(a) * d}px`);
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 750);
    }
  };
  document.querySelectorAll('.btn-gold').forEach((b) => b.addEventListener('click', (e) => burst(e.clientX, e.clientY)));

  // Before / after slider
  document.querySelectorAll('.ba').forEach((ba) => {
    const input = ba.querySelector('input');
    let shone = false;
    const set = () => {
      const v = +input.value;
      ba.style.setProperty('--pos', `${v}%`);
      if (v <= 3 && !shone) {
        shone = true; ba.classList.add('shine');
        const r = ba.getBoundingClientRect();
        for (let k = 0; k < 4; k++) setTimeout(() => burst(r.left + r.width * (0.2 + Math.random() * 0.6), r.top + r.height * (0.45 + Math.random() * 0.4), 6, 60), k * 120);
      }
      if (v > 12 && shone) { shone = false; ba.classList.remove('shine'); }
    };
    input.addEventListener('input', set); set();
  });

  // gentle parallax on service hero photo
  const ph = document.querySelector('.s-photo');
  if (ph && fine && !reduce) {
    let raf = 0;
    addEventListener('scroll', () => {
      if (raf) return;
      raf = requestAnimationFrame(() => { ph.style.setProperty('--py', `${Math.min(scrollY, 600) * 0.06}px`); raf = 0; });
    }, { passive: true });
  }

  // WhatsApp lead form
  const form = document.getElementById('lead');
  if (form) form.addEventListener('submit', (e) => {
    e.preventDefault();
    const f = new FormData(form);
    const phone = form.querySelector('[name=phone]');
    const ok = /^0\d{8,9}$/.test(String(f.get('phone')).replace(/[\s-]/g, ''));
    phone.setAttribute('aria-invalid', ok ? 'false' : 'true');
    if (!ok) { phone.focus(); return; }
    const lines = [
      'שלום ג׳מבו קלין, אשמח להצעת מחיר.',
      `שם: ${f.get('name') || ''}`,
      `טלפון: ${f.get('phone')}`,
      `שירות: ${f.get('service')}`,
      f.get('city') ? `עיר: ${f.get('city')}` : '',
      f.get('msg') ? `פרטים: ${f.get('msg')}` : '',
    ].filter(Boolean);
    window.open(`https://wa.me/972528580800?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener');
  });
})();
