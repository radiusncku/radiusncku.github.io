/* ============================================================
   RADIUS Lab — language toggle (English / 繁體中文)
   ------------------------------------------------------------
   Sets data-lang on the <html> element. CSS in styles.css
   shows the matching language and hides the other.
   The choice is saved, so it carries across pages and reloads.
   ============================================================ */
(function () {
  var STORAGE_KEY = 'radius-lang';
  var root = document.documentElement;

  function getSaved() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }
  function setLang(lang) {
    root.setAttribute('data-lang', lang);
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
  }

  // Apply the saved language as early as possible (default: English).
  setLang(getSaved() === 'zh' ? 'zh' : 'en');

  // Any element with [data-lang-toggle] flips the language when clicked.
  document.addEventListener('click', function (e) {
    var toggle = e.target.closest('[data-lang-toggle]');
    if (!toggle) return;
    e.preventDefault();
    setLang(root.getAttribute('data-lang') === 'en' ? 'zh' : 'en');
  });
})();
