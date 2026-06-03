// Shared helpers for guided slash-command tours.

const TOUR_STYLES =
  '#tour-tooltip{position:fixed;z-index:10001;background:var(--bg);color:var(--fg);' +
  'border:1px solid var(--border);border-radius:8px;padding:12px 14px;max-width:280px;' +
  'font-family:inherit;font-size:0.8rem;line-height:1.5;' +
  'box-shadow:0 2px 12px rgba(0,0,0,0.3);pointer-events:auto;' +
  'opacity:0;transform:translateY(4px);transition:opacity 0.3s ease-out,transform 0.3s ease-out}' +
  '#tour-tooltip.tour-fade-in{opacity:1;transform:translateY(0)}' +
  '#tour-tooltip .tour-text{margin-bottom:8px;opacity:0.8}' +
  '.tour-nav{display:flex;align-items:center;justify-content:space-between}' +
  '.tour-nav button{background:none;border:1px solid var(--border);color:var(--fg);' +
  'cursor:pointer;font-family:inherit;border-radius:4px;transition:all .1s}' +
  '.tour-nav button:hover{background:color-mix(in srgb,var(--fg) 8%,transparent)}' +
  '.tour-btn-arrow{font-size:1rem;padding:4px 12px;opacity:0.6}' +
  '.tour-btn-arrow:hover{opacity:1}' +
  '.tour-btn-arrow.disabled{opacity:0.15;pointer-events:none}' +
  '.tour-btn-skip{font-size:0.72rem;padding:3px 10px;opacity:0.35;border-color:transparent!important}' +
  '.tour-btn-skip:hover{opacity:0.6}';

export function ensureTourStyles() {
  if (document.getElementById('tour-styles')) return;
  const style = document.createElement('style');
  style.id = 'tour-styles';
  style.textContent = TOUR_STYLES;
  document.head.appendChild(style);
}

export function clearTourCommandInput() {
  const msgEl = document.getElementById('message');
  if (!msgEl) return;
  msgEl.value = '';
  msgEl.dispatchEvent(new Event('input', { bubbles: true }));
}

export function createTourSession() {
  ensureTourStyles();
  document.body.classList.add('tour-active');

  document.getElementById('tour-tooltip')?.remove();
  const tooltip = document.createElement('div');
  tooltip.id = 'tour-tooltip';
  document.body.appendChild(tooltip);

  let halos = [];

  function makeHalo(target) {
    const halo = document.createElement('div');
    halo.className = 'tour-halo';
    document.body.appendChild(halo);

    const update = () => {
      const r = target.getBoundingClientRect();
      halo.style.top = (r.top - 4) + 'px';
      halo.style.left = (r.left - 4) + 'px';
      halo.style.width = (r.width + 8) + 'px';
      halo.style.height = (r.height + 8) + 'px';
    };

    update();
    window.addEventListener('resize', update);
    window.addEventListener('scroll', update, true);
    requestAnimationFrame(() => halo.classList.add('tour-fade-in'));

    return {
      destroy() {
        window.removeEventListener('resize', update);
        window.removeEventListener('scroll', update, true);
        halo.remove();
      },
    };
  }

  function clearHalos() {
    halos.forEach(h => h.destroy());
    halos = [];
    document.querySelectorAll('.tour-halo').forEach(e => e.remove());
  }

  function addHalo(target) {
    const halo = makeHalo(target);
    halos.push(halo);
    return halo;
  }

  function positionTooltip(target, placement) {
    tooltip.style.visibility = 'hidden';
    tooltip.style.display = '';
    const tw = tooltip.offsetWidth || 260;
    const th = tooltip.offsetHeight || 100;

    if (placement === 'center-above') {
      const top = Math.max(10, window.innerHeight * 0.32 - th / 2);
      const left = Math.max(10, window.innerWidth / 2 - tw / 2);
      tooltip.style.top = top + 'px';
      tooltip.style.left = left + 'px';
      tooltip.style.visibility = '';
      return;
    }

    const r = target.getBoundingClientRect();
    const gap = 12;
    let top;
    let left;

    if (r.bottom + gap + th < window.innerHeight - 10) {
      top = r.bottom + gap;
      left = r.left + r.width / 2 - tw / 2;
    } else if (r.top - gap - th > 10) {
      top = r.top - gap - th;
      left = r.left + r.width / 2 - tw / 2;
    } else {
      top = r.top + r.height / 2 - th / 2;
      left = r.right + gap;
      if (left + tw > window.innerWidth - 10) left = r.left - tw - gap;
    }

    if (left + tw > window.innerWidth - 10) left = window.innerWidth - tw - 10;
    if (left < 10) left = 10;
    if (top < 10) top = 10;
    tooltip.style.top = top + 'px';
    tooltip.style.left = left + 'px';
    tooltip.style.visibility = '';
  }

  function clear() {
    document.querySelectorAll('.odysseus-highlight').forEach(e => e.classList.remove('odysseus-highlight'));
    clearHalos();
    tooltip.remove();
    document.body.classList.remove('tour-active');
  }

  return { tooltip, addHalo, clearHalos, positionTooltip, clear };
}

export function showTourStep(session, sel, text, opts = {}) {
  const isFirst = !!opts.isFirst;
  const isLast = !!opts.isLast;
  const before = opts.before;
  const placement = opts.placement;
  const extraSel = opts.extraSel;
  const interactive = !!opts.interactive;
  const delayMs = opts.delayMs || 0;

  return new Promise(resolve => {
    session.clearHalos();
    if (before) {
      try { before(); } catch (_) {}
    }

    setTimeout(() => {
      const target = document.querySelector(sel);
      if (!target) return resolve('skip');
      session.addHalo(target);
      const extra = extraSel ? document.querySelector(extraSel) : null;
      if (extra) session.addHalo(extra);
      target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

      session.tooltip.classList.remove('tour-fade-in');
      session.tooltip.innerHTML =
        '<div class="tour-text">' + text + '</div>' +
        '<div class="tour-nav">' +
          '<button class="tour-btn-arrow' + (isFirst ? ' disabled' : '') + '" data-act="back">←</button>' +
          '<button class="tour-btn-skip" data-act="skip">' + (isLast ? 'done' : 'skip tour') + '</button>' +
          '<button class="tour-btn-arrow" data-act="next">' + (isLast ? '✓' : '→') + '</button>' +
        '</div>';

      requestAnimationFrame(() => {
        session.positionTooltip(target, placement);
        session.tooltip.classList.add('tour-fade-in');
      });

      let onTarget;
      const cleanup = () => {
        session.tooltip.removeEventListener('click', onClick);
        if (onTarget) {
          target.removeEventListener('click', onTarget, true);
          if (extra) extra.removeEventListener('click', onTarget, true);
        }
      };
      const onClick = (e) => {
        const hit = e.target.closest && e.target.closest('[data-act]');
        const act = hit && hit.dataset.act;
        if (!act) return;
        cleanup();
        resolve(act);
      };

      session.tooltip.addEventListener('click', onClick);
      if (interactive) {
        onTarget = () => { cleanup(); resolve('next'); };
        target.addEventListener('click', onTarget, true);
        if (extra) extra.addEventListener('click', onTarget, true);
      }
    }, delayMs);
  });
}
