/* ============================================================
   Blog Infirmier — JavaScript Principal
   ============================================================ */

'use strict';

// ── Back to top ──────────────────────────────────────────────
(function () {
  const btn = document.getElementById('backToTop');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('show', window.scrollY > 400);
  });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
})();

// ── Auto-dismiss flash messages ───────────────────────────────
(function () {
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert && bsAlert.close();
    }, 5000);
  });
})();

// ── Navbar glassmorphism on scroll ───────────────────────────────
(function () {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
    nav.classList.toggle('navbar-shrunk', window.scrollY > 50);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

// ── Search form UX ────────────────────────────────────────────
(function () {
  const searchInputs = document.querySelectorAll('input[type="search"]');
  searchInputs.forEach(input => {
    // Highlight on focus
    input.addEventListener('focus', () => input.closest('.input-group')?.classList.add('focused'));
    input.addEventListener('blur', () => input.closest('.input-group')?.classList.remove('focused'));
  });
})();

// ── Character counter for meta fields ─────────────────────────
(function () {
  document.querySelectorAll('textarea[maxlength], input[maxlength]').forEach(el => {
    const max = parseInt(el.getAttribute('maxlength'));
    if (!max) return;
    const counter = document.createElement('small');
    counter.className = 'text-muted d-block text-end mt-1';
    counter.textContent = `${el.value.length} / ${max}`;
    el.parentNode.appendChild(counter);
    el.addEventListener('input', () => {
      const len = el.value.length;
      counter.textContent = `${len} / ${max}`;
      counter.classList.toggle('text-danger', len > max * 0.9);
    });
  });
})();

// ── Smooth scroll for anchor links ───────────────────────────
(function () {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = document.querySelector('.navbar')?.offsetHeight || 70;
        window.scrollTo({ top: target.offsetTop - offset - 16, behavior: 'smooth' });
      }
    });
  });
})();

// ── Image lazy loading fallback ───────────────────────────────
(function () {
  if ('loading' in HTMLImageElement.prototype) return; // native lazy loading supported
  const lazyImages = document.querySelectorAll('img[loading="lazy"]');
  const io = new IntersectionObserver(entries => {
    entries.forEach(({ isIntersecting, target }) => {
      if (isIntersecting) {
        target.src = target.dataset.src || target.src;
        io.unobserve(target);
      }
    });
  });
  lazyImages.forEach(img => io.observe(img));
})();

// ── Copy to clipboard utility ─────────────────────────────────
window.copyToClipboard = function (text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Lien copié dans le presse-papiers !', 'success');
  }).catch(() => {
    showToast('Impossible de copier le lien.', 'danger');
  });
};

// ── Toast notifications ───────────────────────────────────────
window.showToast = function (message, type = 'info') {
  const container = document.getElementById('toast-container') || (() => {
    const c = document.createElement('div');
    c.id = 'toast-container';
    c.className = 'position-fixed bottom-0 end-0 p-3';
    c.style.zIndex = '9999';
    document.body.appendChild(c);
    return c;
  })();

  const id = 'toast-' + Date.now();
  const icons = { success: 'check-circle-fill', danger: 'exclamation-triangle-fill', info: 'info-circle-fill', warning: 'exclamation-circle-fill' };
  container.insertAdjacentHTML('beforeend', `
    <div id="${id}" class="toast align-items-center text-bg-${type} border-0 show" role="alert">
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-${icons[type] || 'info-circle-fill'} me-2"></i>${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  `);
  setTimeout(() => document.getElementById(id)?.remove(), 4000);
};

// ── Newsletter form AJAX ───────────────────────────────────────
(function () {
  const form = document.querySelector('form[action*="newsletter"]');
  if (!form) return;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    const original = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>...';
    btn.disabled = true;
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value }
      });
      showToast(res.ok ? 'Inscription réussie !' : 'Erreur lors de l\'inscription.', res.ok ? 'success' : 'danger');
      if (res.ok) form.reset();
    } catch {
      showToast('Erreur réseau.', 'danger');
    } finally {
      btn.innerHTML = original;
      btn.disabled = false;
    }
  });
})();

// ── Reading progress bar ──────────────────────────────────────
(function () {
  if (!document.querySelector('.article-content')) return;
  const bar = document.createElement('div');
  bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:var(--medical-blue);z-index:9999;transition:width .1s;width:0';
  document.body.appendChild(bar);
  window.addEventListener('scroll', () => {
    const el = document.documentElement;
    const pct = (el.scrollTop / (el.scrollHeight - el.clientHeight)) * 100;
    bar.style.width = Math.min(100, pct) + '%';
  });
})();

// ── Table of contents highlight on scroll ─────────────────────
(function () {
  const tocLinks = document.querySelectorAll('#toc a');
  if (!tocLinks.length) return;
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        tocLinks.forEach(l => l.classList.remove('text-primary', 'fw-semibold'));
        const active = document.querySelector(`#toc a[href="#${entry.target.id}"]`);
        active?.classList.add('text-primary', 'fw-semibold');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  document.querySelectorAll('.article-content h2, .article-content h3').forEach(h => observer.observe(h));
})();
