# -*- coding: utf-8 -*-
"""
Gabarit HTML partagé pour les articles de blog générés automatiquement.
Reprend exactement la structure/CSS du site (header, footer, script WhatsApp)
pour que les articles auto-générés soient visuellement identiques aux articles existants.
"""

BASE = "https://karnett.fr"
WA_NUMBER = "33782107303"

HEAD_COMMON = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/karnett.css">
"""

HEADER_NAV = """<a href="{root}#main" class="skip-link">Aller au contenu principal</a>

<header>
  <div class="wrap nav">
    <a href="{root}" class="logo"><span class="logo-mark"><span>K</span></span>Karnett</a>
    <nav class="nav-links" aria-label="Navigation principale">
      <a href="{root}#services">Prestations</a>
      <a href="{root}#tarifs">Tarifs</a>
      <a href="{root}zones-desservies.html">Villes</a>
      <a href="{root}blog/">Blog</a>
      <a href="{root}#faq">FAQ</a>
    </nav>
    <div class="nav-cta">
      <a href="{root}#tarifs" class="btn btn-ghost btn-small">Voir les tarifs</a>
      <a id="waNavBtn" href="#" class="btn btn-primary btn-small">Devis WhatsApp</a>
      <button class="nav-toggle" id="navToggle" aria-label="Ouvrir le menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>

<div class="mobile-menu" id="mobileMenu">
  <a href="{root}#services">Prestations</a>
  <a href="{root}#tarifs">Tarifs</a>
  <a href="{root}zones-desservies.html">Villes desservies</a>
  <a href="{root}blog/">Blog</a>
  <a href="{root}#faq">FAQ</a>
  <a id="waMobileBtn" href="#" class="btn btn-wa">Demander un devis sur WhatsApp</a>
</div>
"""

FOOTER = """<footer>
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <a href="{root}" class="logo"><span class="logo-mark"><span>K</span></span>Karnett</a>
        <p>Nettoyage intérieur automobile à domicile. Basé à Montereau-Fault-Yonne, intervention dans le sud de la Seine-et-Marne.</p>
      </div>
      <nav class="footer-col" aria-label="Prestations">
        <div class="k">Prestations</div>
        <a href="{root}#services">Aspiration &amp; sols</a>
        <a href="{root}#services">Plastiques &amp; vitres</a>
        <a href="{root}#services">Sièges &amp; odeurs</a>
        <a href="{root}#tarifs">Tarifs</a>
      </nav>
      <nav class="footer-col" aria-label="Villes desservies">
        <div class="k">Villes desservies</div>
        <a href="{root}nettoyage-voiture-montereau-fault-yonne.html">Montereau-Fault-Yonne</a>
        <a href="{root}nettoyage-voiture-melun.html">Melun</a>
        <a href="{root}nettoyage-voiture-fontainebleau.html">Fontainebleau</a>
        <a href="{root}zones-desservies.html">Toutes les villes</a>
      </nav>
      <nav class="footer-col" aria-label="Informations">
        <div class="k">Infos</div>
        <a href="{root}blog/">Blog</a>
        <a href="{root}#faq">FAQ</a>
        <a href="{root}#contact">Contact</a>
      </nav>
    </div>

    <p class="footer-legal">
      <strong>Mentions légales</strong> — Karnett, entreprise individuelle (auto-entrepreneur). Basé à Montereau-Fault-Yonne (77130). Contact : 07 82 10 73 03. Directeur de la publication : le gérant de Karnett. Hébergement : Netlify, Inc., 512 2nd Street, San Francisco, CA 94107, USA. SIRET : à compléter.<br>
      <strong>Confidentialité</strong> — Les informations que vous transmettez via WhatsApp ou par téléphone sont utilisées uniquement pour répondre à votre demande de devis et organiser la prestation. Elles ne sont ni revendues ni transmises à des tiers. Vous pouvez demander leur suppression à tout moment.
    </p>

    <div class="footer-bottom">
      <span>© 2026 Karnett. Tous droits réservés.</span>
      <span>Nettoyage intérieur automobile · Sud Seine-et-Marne</span>
    </div>
  </div>
</footer>
"""

SCRIPT = """<script>
  var WHATSAPP_NUMBER = "{wa}";
  function waLink(msg){{ return "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(msg); }}
  var msgGeneric = "{msg_generic}";
  document.getElementById('waNavBtn').href = waLink(msgGeneric);
  document.getElementById('waMobileBtn').href = waLink(msgGeneric);
  {extra_js}
  var navToggle = document.getElementById('navToggle');
  var mobileMenu = document.getElementById('mobileMenu');
  navToggle.addEventListener('click', function(){{
    var open = mobileMenu.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }});
  mobileMenu.querySelectorAll('a').forEach(function(a){{
    a.addEventListener('click', function(){{ mobileMenu.classList.remove('open'); navToggle.setAttribute('aria-expanded','false'); }});
  }});
  var io = new IntersectionObserver(function(entries){{
    entries.forEach(function(entry){{ if(entry.isIntersecting){{ entry.target.classList.add('in'); io.unobserve(entry.target); }} }});
  }}, {{ threshold: 0.12 }});
  document.querySelectorAll('.reveal').forEach(function(el){{ io.observe(el); }});
</script>
"""

def page_shell(root, title, description, canonical, og_image, body_html, schema_json, extra_js="", wa_msg=None):
    if wa_msg is None:
        wa_msg = "Bonjour Karnett, je souhaite un devis pour le nettoyage intérieur de ma voiture. Véhicule : ... / Ville : ... / Formule souhaitée : ..."
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0A0A0A">
<link rel="icon" type="image/svg+xml" href="{root}images/karnett-icon.svg">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Karnett">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="fr_FR">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">

{HEAD_COMMON.format(root=root)}
<script type="application/ld+json">
{schema_json}
</script>
</head>
<body>
{HEADER_NAV.format(root=root)}
<main id="main">
{body_html}
</main>
{FOOTER.format(root=root)}
{SCRIPT.format(wa=WA_NUMBER, msg_generic=wa_msg, extra_js=extra_js)}
</body>
</html>
"""
