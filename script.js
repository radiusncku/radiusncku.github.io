/* ============================================================
   RADIUS Lab — small site behaviours (no libraries)
   1) English / 繁體中文 language toggle (remembered across pages)
   2) Mobile navigation menu (hamburger)
   3) Scroll-reveal animations (fade + rise as sections enter view)
   ============================================================ */
(function () {
  var root = document.documentElement;

  /* ---- 1) Language toggle -------------------------------------------- */
  var STORAGE_KEY = 'radius-lang';
  function getSaved() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }
  function setLang(lang) {
    root.setAttribute('data-lang', lang);
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
  }
  setLang(getSaved() === 'zh' ? 'zh' : 'en');

  /* ---- 2) Mobile menu + language toggle clicks ----------------------- */
  document.addEventListener('click', function (e) {
    var langBtn = e.target.closest('[data-lang-toggle]');
    if (langBtn) {
      e.preventDefault();
      setLang(root.getAttribute('data-lang') === 'en' ? 'zh' : 'en');
      return;
    }
    var navBtn = e.target.closest('[data-nav-toggle]');
    if (navBtn) {
      var links = document.querySelector('.nav-links');
      if (links) {
        var open = links.classList.toggle('open');
        navBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
      return;
    }
    // Tapping a normal nav link closes the mobile menu.
    if (e.target.closest('.nav-links a')) {
      var l = document.querySelector('.nav-links.open');
      if (l) l.classList.remove('open');
    }
  });

  /* ---- 3) Scroll-reveal animations ----------------------------------- */
  function initReveal() {
    var selectors = [
      '.hero-title', '.hero-sub', '.hero-actions', '.eyebrow', '.section-title',
      '.about-body', '.research-item', '.pub-group', '.member-group',
      '.member', '.news-item', '.pi', '.tt-block', '.res-item',
      '.join .container > div'
    ];
    var nodes = document.querySelectorAll(selectors.join(','));
    if (!('IntersectionObserver' in window) || !nodes.length) return;

    nodes.forEach(function (n) { n.classList.add('reveal'); });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });

    nodes.forEach(function (n) { io.observe(n); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReveal);
  } else {
    initReveal();
  }
})();
