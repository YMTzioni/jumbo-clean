// Accessibility preferences panel (Regulation 35 / IS 5568 comfort tool).
// It only toggles classes on <html>; it never rewrites page content.
(() => {
  const KEY = 'jc_a11y_v1';
  const DEF = { v: 1, text: 100, lines: 0, contrast: 'off', links: false, heads: false, font: false, cursor: false, motion: false };
  const TEXT = [100, 115, 130, 150];
  const LINES = [0, 16, 20];
  const CONTRAST = ['off', 'high', 'invert', 'mono'];
  const CONTRAST_LABEL = { off: 'רגילה', high: 'גבוהה', invert: 'צבעים הפוכים', mono: 'שחור לבן' };

  const load = () => {
    try { const p = JSON.parse(localStorage.getItem(KEY)); return p && p.v === 1 ? { ...DEF, ...p } : { ...DEF }; }
    catch (e) { return { ...DEF }; }
  };
  let p = load();
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { /* storage blocked */ } };

  // keep in sync with the bootstrap script in <head> (tools/build.py A11Y_BOOT)
  const apply = () => {
    const c = document.documentElement.classList;
    TEXT.slice(1).forEach((t) => c.toggle(`a11y-text-${t}`, p.text === t));
    LINES.slice(1).forEach((l) => c.toggle(`a11y-lines-${l}`, p.lines === l));
    CONTRAST.slice(1).forEach((k) => c.toggle(`a11y-contrast-${k}`, p.contrast === k));
    c.toggle('a11y-links', p.links); c.toggle('a11y-heads', p.heads); c.toggle('a11y-font', p.font);
    c.toggle('a11y-cursor', p.cursor); c.toggle('a11y-motion', p.motion);
  };

  const panel = document.getElementById('a11y-panel');
  const trigger = document.getElementById('a11y-trigger');
  const live = document.getElementById('a11y-live');
  if (!panel || !trigger) { apply(); return; }

  const controls = [
    { id: 'text', label: 'גודל טקסט', cycle: TEXT, val: () => `${p.text}%` },
    { id: 'lines', label: 'ריווח שורות', cycle: LINES, val: () => (p.lines ? (p.lines / 10).toFixed(1) : 'רגיל') },
    { id: 'contrast', label: 'ניגודיות', cycle: CONTRAST, val: () => CONTRAST_LABEL[p.contrast] },
    { id: 'links', label: 'הדגשת קישורים' },
    { id: 'heads', label: 'הדגשת כותרות' },
    { id: 'font', label: 'גופן קריא' },
    { id: 'cursor', label: 'סמן גדול' },
    { id: 'motion', label: 'עצירת אנימציות' },
  ];

  const grid = panel.querySelector('.a11y-grid');
  const render = () => {
    grid.innerHTML = '';
    controls.forEach((ctl) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'a11y-opt';
      if (ctl.cycle) {
        const v = ctl.val();
        b.setAttribute('aria-label', `${ctl.label}: ${v}`);
        b.innerHTML = `<b>${ctl.label}</b><span>${v}</span>`;
        b.classList.toggle('on', p[ctl.id] !== ctl.cycle[0]);
      } else {
        b.setAttribute('aria-pressed', String(!!p[ctl.id]));
        b.innerHTML = `<b>${ctl.label}</b><span>${p[ctl.id] ? 'פעיל' : 'כבוי'}</span>`;
        b.classList.toggle('on', !!p[ctl.id]);
      }
      b.addEventListener('click', () => {
        if (ctl.cycle) { const i = ctl.cycle.indexOf(p[ctl.id]); p[ctl.id] = ctl.cycle[(i + 1) % ctl.cycle.length]; }
        else p[ctl.id] = !p[ctl.id];
        save(); apply(); render();
        grid.querySelectorAll('.a11y-opt')[controls.indexOf(ctl)].focus();
        live.textContent = ctl.cycle ? `${ctl.label}: ${ctl.val()}` : `${ctl.label} ${p[ctl.id] ? 'הופעל' : 'כובה'}`;
      });
      grid.appendChild(b);
    });
  };

  panel.querySelector('[data-a11y-reset]').addEventListener('click', () => {
    p = { ...DEF }; save(); apply(); render(); live.textContent = 'הגדרות הנגישות אופסו';
  });

  const focusables = () => [...panel.querySelectorAll('button, a[href]')];
  const open = (state) => {
    panel.hidden = !state;
    trigger.setAttribute('aria-expanded', String(state));
    if (state) focusables()[0].focus(); else trigger.focus();
  };
  trigger.addEventListener('click', () => open(panel.hidden));
  panel.querySelector('[data-a11y-close]').addEventListener('click', () => open(false));
  panel.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { e.preventDefault(); open(false); }
    if (e.key === 'Tab') {
      const f = focusables(); const first = f[0]; const last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.altKey && !e.ctrlKey && !e.metaKey && !e.shiftKey && e.code === 'KeyA') { e.preventDefault(); open(panel.hidden); }
  });

  apply(); render();
})();
