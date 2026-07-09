# -*- coding: utf-8 -*-
"""
Génère automatiquement un nouvel article de blog Karnett :
1. Lit content-plan/300-idees-articles-blog.md et choisit la prochaine idée non publiée
2. Appelle l'API Claude pour rédiger l'article (contenu + FAQ + méta) en JSON structuré
3. Génère le fichier HTML final avec le même gabarit que le reste du site
4. Met à jour sitemap.xml et blog/index.html
5. Marque l'idée comme publiée dans blog/_published_ideas.json

Ce script est appelé automatiquement chaque semaine par GitHub Actions.
Il ne pousse jamais directement sur main : le workflow l'exécute sur une branche
à part et ouvre une Pull Request, pour permettre une relecture avant mise en ligne.
"""

import json
import os
import re
import sys
import unicodedata
import urllib.request
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from blog_template import page_shell, BASE

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IDEAS_FILE = os.path.join(REPO_ROOT, "content-plan", "300-idees-articles-blog.md")
PUBLISHED_TRACK = os.path.join(REPO_ROOT, "blog", "_published_ideas.json")
SITEMAP_FILE = os.path.join(REPO_ROOT, "sitemap.xml")
BLOG_INDEX_FILE = os.path.join(REPO_ROOT, "blog", "index.html")
BLOG_DIR = os.path.join(REPO_ROOT, "blog")

# Villes disponibles pour le maillage interne (doit rester cohérent avec city_data.py)
CITY_SLUGS = {
    "Montereau-Fault-Yonne": "nettoyage-voiture-montereau-fault-yonne",
    "Melun": "nettoyage-voiture-melun",
    "Fontainebleau": "nettoyage-voiture-fontainebleau",
    "Nemours": "nettoyage-voiture-nemours",
    "Provins": "nettoyage-voiture-provins",
    "Sens": "nettoyage-voiture-sens",
    "Dammarie-lès-Lys": "nettoyage-voiture-dammarie-les-lys",
    "Avon": "nettoyage-voiture-avon",
    "Moret-Loing-et-Orvanne": "nettoyage-voiture-moret-loing-et-orvanne",
    "Bois-le-Roi": "nettoyage-voiture-bois-le-roi",
    "Héricy": "nettoyage-voiture-hericy",
    "Samoreau": "nettoyage-voiture-samoreau",
    "Champagne-sur-Seine": "nettoyage-voiture-champagne-sur-seine",
    "Nangis": "nettoyage-voiture-nangis",
    "Bray-sur-Seine": "nettoyage-voiture-bray-sur-seine",
}

FRENCH_MONTHS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def format_date_fr(d):
    """Formate une date en français lisible : 9 juillet 2026"""
    return f"{d.day} {FRENCH_MONTHS[d.month - 1]} {d.year}"


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-+", "-", text)
    return text[:80]


def load_ideas():
    with open(IDEAS_FILE, encoding="utf-8") as f:
        content = f.read()
    ideas = []
    for line in content.split("\n"):
        m = re.match(r"^\d+\.\s+(.*)$", line.strip())
        if m:
            ideas.append(m.group(1).strip())
    return ideas


def load_published():
    if os.path.exists(PUBLISHED_TRACK):
        with open(PUBLISHED_TRACK, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_published(published):
    os.makedirs(os.path.dirname(PUBLISHED_TRACK), exist_ok=True)
    with open(PUBLISHED_TRACK, "w", encoding="utf-8") as f:
        json.dump(published, f, ensure_ascii=False, indent=2)


def pick_next_idea():
    ideas = load_ideas()
    published = load_published()
    for idea in ideas:
        if idea not in published:
            return idea
    return None  # toutes les idées ont été utilisées


def call_claude(idea):
    api_key = os.environ["ANTHROPIC_API_KEY"]
    city_names = list(CITY_SLUGS.keys())

    system_prompt = f"""Tu écris un article de blog SEO pour Karnett, une entreprise de nettoyage
intérieur automobile à domicile basée à Montereau-Fault-Yonne (Seine-et-Marne, France),
qui intervient aussi à Melun, Fontainebleau, Nemours, Provins, Sens et une quinzaine
d'autres communes du sud Seine-et-Marne. Trois formules existent : Express (29€), Complet (49€),
Premium (79€, avec shampouinage des sièges).

Ton : professionnel, direct, jamais survendeur. Phrases courtes. Pas de remplissage.
Longueur du corps de l'article : 500 à 700 mots, en français.
Structure : un court paragraphe d'intro, puis 3 à 5 sections avec des titres H2,
puis une FAQ de 3 questions/réponses courtes.
Choisis 2 villes parmi cette liste pour les liens internes (les plus pertinentes pour le sujet) : {", ".join(city_names)}.

Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant/après, sans balises markdown, au format exact :
{{
  "title": "titre H1 accrocheur, 50-65 caractères",
  "meta_description": "meta description SEO, 140-160 caractères",
  "excerpt": "résumé d'1 phrase pour la liste du blog",
  "body_html": "le corps de l'article en HTML : des balises <h2>, <p>, <ul><li> uniquement, PAS de <html>/<head>/<body>, PAS de <h1>",
  "faq": [["question 1", "réponse 1"], ["question 2", "réponse 2"], ["question 3", "réponse 3"]],
  "cities": ["Ville A", "Ville B"]
}}"""

    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 3000,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": f"Sujet de l'article : {idea}"}
        ],
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    text = "".join(block["text"] for block in data["content"] if block["type"] == "text")
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def build_article_html(slug, article):
    canonical = f"{BASE}/blog/{slug}.html"
    title = f"{article['title']} | Blog Karnett"
    description = article["meta_description"]
    og_image = f"{BASE}/images/avant-apres-1.webp"
    today_iso = date.today().isoformat()
    today_fr = format_date_fr(date.today())

    city_links = ""
    for city in article.get("cities", [])[:2]:
        city_slug = CITY_SLUGS.get(city)
        if city_slug:
            city_links += f'<li><a href="{BASE}/{city_slug}.html">Nettoyage intérieur voiture à {city}</a></li>'

    body = f"""
  <div class="wrap">
    <nav class="breadcrumb" aria-label="Fil d'Ariane">
      <a href="{BASE}/">Accueil</a> / <a href="{BASE}/blog/">Blog</a> / <span>{article['title']}</span>
    </nav>
  </div>

  <article class="page-hero wrap">
    <div class="eyebrow">Blog Karnett</div>
    <h1>{article['title']}</h1>
    <p class="article-date">Publié le <time datetime="{today_iso}">{today_fr}</time> · <span class="article-date-relative" data-published="{today_iso}">à l'instant</span></p>
    <p class="lead">{article['excerpt']}</p>
  </article>

  <section class="section alt">
    <div class="wrap content-block">
{article['body_html']}
      <div class="inline-cta">
        <p>Un devis rapide et sans engagement, directement sur WhatsApp.</p>
        <a id="waCtaBtn" href="#" class="btn btn-wa btn-small">Demander un devis</a>
      </div>

      <h2>Villes concernées par cet article</h2>
      <ul>
        {city_links}
      </ul>
    </div>
  </section>

  <section class="section" id="faq-article" aria-labelledby="faq-article-h2">
    <div class="wrap">
      <div class="section-head reveal">
        <div class="eyebrow">Questions fréquentes</div>
        <h2 id="faq-article-h2">Questions sur le sujet</h2>
      </div>
      <div class="faq-list reveal">
{"".join(f'''        <details>
          <summary>{q}<span class="faq-icon"></span></summary>
          <div class="faq-answer">{a}</div>
        </details>''' for q, a in article["faq"])}
      </div>
    </div>
  </section>

  <section class="cta-band wrap">
    <h2>Votre voiture mérite un intérieur impeccable.</h2>
    <p>Devis rapide, sans engagement, directement sur WhatsApp.</p>
    <div class="cta-actions">
      <a id="waFinalBtn" href="#" class="btn btn-wa">Demander un devis sur WhatsApp</a>
      <a href="{BASE}/blog/" class="btn btn-ghost">Voir tous les articles</a>
    </div>
  </section>
"""

    faq_schema_entities = ",".join(
        f'{{"@type":"Question","name":{json.dumps(q, ensure_ascii=False)},"acceptedAnswer":{{"@type":"Answer","text":{json.dumps(a, ensure_ascii=False)}}}}}'
        for q, a in article["faq"]
    )

    schema = f"""{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type":"ListItem","position":1,"name":"Accueil","item":"{BASE}/"}},
        {{"@type":"ListItem","position":2,"name":"Blog","item":"{BASE}/blog/"}},
        {{"@type":"ListItem","position":3,"name":{json.dumps(article['title'], ensure_ascii=False)},"item":"{canonical}"}}
      ]
    }},
    {{
      "@type": "Article",
      "headline": {json.dumps(article['title'], ensure_ascii=False)},
      "description": {json.dumps(description, ensure_ascii=False)},
      "image": "{og_image}",
      "datePublished": "{today_iso}",
      "dateModified": "{today_iso}",
      "author": {{"@type":"Organization","name":"Karnett"}},
      "publisher": {{"@type":"Organization","name":"Karnett","logo":{{"@type":"ImageObject","url":"{BASE}/images/karnett-icon.svg"}}}},
      "mainEntityOfPage": "{canonical}"
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [{faq_schema_entities}]
    }}
  ]
}}"""

    relative_date_js = """
  document.querySelectorAll('.article-date-relative').forEach(function (el) {
    var published = new Date(el.getAttribute('data-published'));
    var now = new Date();
    var diffDays = Math.floor((now - published) / (1000 * 60 * 60 * 24));
    var text;
    if (diffDays <= 0) {
      text = "publié aujourd'hui";
    } else if (diffDays === 1) {
      text = "il y a 1 jour";
    } else if (diffDays < 30) {
      text = "il y a " + diffDays + " jours";
    } else if (diffDays < 365) {
      var months = Math.floor(diffDays / 30);
      text = "il y a " + months + (months === 1 ? " mois" : " mois");
    } else {
      var years = Math.floor(diffDays / 365);
      text = "il y a " + years + (years === 1 ? " an" : " ans");
    }
    el.textContent = text;
  });
"""

    extra_js = (
        "document.getElementById('waCtaBtn').href = waLink(msgGeneric);\n"
        "  document.getElementById('waFinalBtn').href = waLink(msgGeneric);\n"
        + relative_date_js
    )

    return page_shell("../", title, description, canonical, og_image, body, schema, extra_js=extra_js)


def update_sitemap(slug):
    with open(SITEMAP_FILE, encoding="utf-8") as f:
        content = f.read()
    new_entry = f"""  <url>
    <loc>{BASE}/blog/{slug}.html</loc>
    <lastmod>{date.today().isoformat()}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>"""
    content = content.replace("</urlset>", new_entry)
    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def update_blog_index(slug, article):
    with open(BLOG_INDEX_FILE, encoding="utf-8") as f:
        content = f.read()
    new_card = f"""<a class="article-card" href="{BASE}/blog/{slug}.html">
          <div class="eyebrow">Nettoyage auto</div>
          <h3>{article['title']}</h3>
          <p>{article['excerpt']}</p>
        </a>"""
    marker = '<div class="article-list reveal">'
    content = content.replace(marker, marker + "\n        " + new_card, 1)
    with open(BLOG_INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    idea = pick_next_idea()
    if idea is None:
        print("Toutes les idées de content-plan ont déjà été publiées. Rien à faire.")
        return

    print("Idée choisie :", idea)
    article = call_claude(idea)
    slug = slugify(article["title"])

    dest = os.path.join(BLOG_DIR, f"{slug}.html")
    if os.path.exists(dest):
        slug = slug + "-" + date.today().isoformat()
        dest = os.path.join(BLOG_DIR, f"{slug}.html")

    html_out = build_article_html(slug, article)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html_out)
    print("Article écrit :", dest)

    update_sitemap(slug)
    update_blog_index(slug, article)

    published = load_published()
    published.append(idea)
    save_published(published)

    print("Terminé. Idée marquée comme publiée :", idea)


if __name__ == "__main__":
    main()
