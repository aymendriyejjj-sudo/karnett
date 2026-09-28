(function () {
  'use strict';
  var KEY = 'karnett-analytics-consent';
  var ID = 'G-9VN0EJS7SR';
  var loaded = false;

  function readChoice() {
    try { return localStorage.getItem(KEY); } catch (_) { return null; }
  }
  function saveChoice(value) {
    try { localStorage.setItem(KEY, value); } catch (_) { /* Ask again next visit. */ }
  }
  function loadAnalytics() {
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', ID);
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
    document.head.appendChild(script);
  }
  function removeAnalyticsCookies() {
    document.cookie.split(';').forEach(function (part) {
      var name = part.trim().split('=')[0];
      if (!/^_ga(?:_|$)/.test(name)) return;
      ['/', location.pathname].forEach(function (path) {
        [location.hostname, '.' + location.hostname, '.karnett.fr'].forEach(function (domain) {
          document.cookie = name + '=; Max-Age=0; path=' + path + '; domain=' + domain + '; SameSite=Lax';
        });
        document.cookie = name + '=; Max-Age=0; path=' + path + '; SameSite=Lax';
      });
    });
  }
  function init() {
    var banner = document.createElement('section');
    banner.className = 'karnett-consent';
    banner.setAttribute('aria-label', 'Choix des cookies');
    banner.innerHTML = '<div class="karnett-consent-inner"><p><strong>Mesure d’audience</strong><br>Karnett utilise Google Analytics pour comprendre la fréquentation du site, uniquement avec votre accord. <a href="/confidentialite.html">En savoir plus</a>.</p><div class="karnett-consent-actions"><button type="button" data-consent="no">Refuser</button><button type="button" data-consent="yes">Accepter</button></div></div>';
    document.body.appendChild(banner);

    var settings = document.createElement('button');
    settings.type = 'button';
    settings.className = 'karnett-consent-settings';
    settings.textContent = 'Gérer les cookies';
    settings.addEventListener('click', function () { banner.hidden = false; });
    var footer = document.querySelector('footer');
    (footer || document.body).appendChild(settings);

    banner.addEventListener('click', function (event) {
      var choice = event.target.getAttribute('data-consent');
      if (!choice) return;
      var previous = readChoice();
      saveChoice(choice);
      banner.hidden = true;
      if (choice === 'yes') loadAnalytics();
      else {
        removeAnalyticsCookies();
        // A loaded tag cannot be unloaded safely; refresh to stop further hits.
        if (previous === 'yes' && loaded) location.reload();
      }
    });
    var choice = readChoice();
    banner.hidden = choice === 'yes' || choice === 'no';
    if (choice === 'yes') loadAnalytics();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
