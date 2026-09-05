#!/usr/bin/env python3
"""
Génère le site H0RS-P1STE à partir des numéros en markdown.

    python3 scripts/build.py

Lit  : contenu/numeros/*.md  +  modeles/*.html
Écrit: public/  (index, archive, un dossier par numéro, flux Atom)

Aucune dépendance externe : bibliothèque standard uniquement.
Le HTML généré est commité dans le dépôt ; Cloudflare Pages sert public/
sans étape de build côté serveur.
"""

import html
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
NUMEROS = RACINE / "contenu" / "numeros"
MODELES = RACINE / "modeles"
PUBLIC = RACINE / "public"

SITE = "https://newsletter.offro4d.ai"
TITRE_SITE = "H0RS-P1STE"
DESCRIPTION_SITE = (
    "La veille hebdomadaire sur l'IA agentique, les fournisseurs de modèles, "
    "les gateways et l'intégration d'entreprise."
)

MOIS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre",
    12: "décembre",
}
JOURS = {
    0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi",
    4: "vendredi", 5: "samedi", 6: "dimanche",
}


# ─────────────────────────────────────────────────────────────
# Lecture des numéros
# ─────────────────────────────────────────────────────────────

def lire_frontmatter(texte):
    """Sépare le frontmatter YAML simple du corps markdown."""
    if not texte.startswith("---"):
        return {}, texte
    fin = texte.find("\n---", 3)
    if fin == -1:
        return {}, texte
    brut, corps = texte[3:fin], texte[fin + 4:]
    meta = {}
    for ligne in brut.splitlines():
        if ":" not in ligne or ligne.strip().startswith("#"):
            continue
        cle, _, val = ligne.partition(":")
        val = val.strip().strip('"').strip("'")
        meta[cle.strip()] = val
    return meta, corps.lstrip("\n")


def charger_numeros():
    numeros = []
    for chemin in sorted(NUMEROS.glob("*.md")):
        meta, corps = lire_frontmatter(chemin.read_text(encoding="utf-8"))
        if meta.get("statut", "publie") != "publie":
            print(f"  … {chemin.name} ignoré (statut: {meta.get('statut')})")
            continue
        meta["date_obj"] = datetime.strptime(meta["date"], "%Y-%m-%d")
        meta["corps"] = corps
        meta["slug"] = meta["numero"]
        numeros.append(meta)
    numeros.sort(key=lambda n: n["numero"], reverse=True)
    return numeros


# ─────────────────────────────────────────────────────────────
# Markdown → HTML (sous-ensemble maîtrisé, pas un parseur général)
# ─────────────────────────────────────────────────────────────

def inline(t):
    """Liens, gras, code, badge « non confirmé »."""
    t = html.escape(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`\[([^\]]+)\]`",
               r'<span class="unconfirmed">\1</span>', t)
    t = re.sub(r"`([^`]+)`", r'<span class="d">\1</span>', t)
    return t


def rendre_corps(md):
    """Convertit le markdown d'un numéro en HTML structuré en balises."""
    lignes = md.split("\n")
    out = []
    i = 0
    dans_balise = False
    dans_article = False
    dans_liste = False
    dans_journal = False
    balise_num = 0

    def fermer_liste():
        nonlocal dans_liste
        if dans_liste:
            out.append("        </ul>")
            dans_liste = False

    def fermer_journal():
        nonlocal dans_journal
        if dans_journal:
            out.append("          </ul>")
            out.append("        </div>")
            dans_journal = False

    def fermer_article():
        nonlocal dans_article
        fermer_journal()
        if dans_article:
            out.append("      </article>")
            dans_article = False

    def fermer_balise():
        nonlocal dans_balise
        fermer_article()
        fermer_liste()
        if dans_balise:
            out.append("    </section>")
            dans_balise = False

    while i < len(lignes):
        l = lignes[i].rstrip()
        i += 1

        if not l.strip():
            continue

        # ## Balise NN · Nom   /   ## Édito
        if l.startswith("## "):
            titre = l[3:].strip()
            if titre.lower().startswith("édito"):
                fermer_balise()
                out.append('  <div class="edito">')
                while i < len(lignes) and not lignes[i].startswith("## "):
                    p = lignes[i].strip()
                    i += 1
                    if p:
                        out.append(f"    <p>{inline(p)}</p>")
                out.append("  </div>")
                out.append("\n  <main>")
                out.append('    <div class="trail" aria-hidden="true"></div>')
                continue

            fermer_balise()
            balise_num += 1
            radar = "radar" if "radar" in titre.lower() else ""
            out.append(f'\n    <section class="balise {radar}">'.replace(" \"", "\""))
            out.append(f'      <span class="balise-tag">{inline(titre)}</span>')
            dans_balise = True
            continue

        # ### Titre de balise
        if l.startswith("### "):
            fermer_article()
            out.append(f"      <h2>{inline(l[4:].strip())}</h2>")
            continue

        # #### Titre d'article
        if l.startswith("#### "):
            fermer_article()
            out.append("\n      <article>")
            out.append(f"        <h3>{inline(l[5:].strip())}</h3>")
            dans_article = True
            continue

        # > Source
        if l.startswith("> "):
            fermer_journal()
            out.append(f'        <span class="src">{inline(l[2:].strip())}</span>')
            continue

        # **Acteur** dans un journal
        if re.fullmatch(r"\*\*[^*]+\*\*", l.strip()):
            fermer_journal()
            acteur = l.strip().strip("*")
            out.append('        <div class="journal">')
            out.append(f'          <div class="acteur">{html.escape(acteur)}</div>')
            out.append("          <ul>")
            dans_journal = True
            continue

        # - item
        if l.lstrip().startswith("- "):
            item = l.lstrip()[2:].strip()
            if dans_journal:
                m = re.match(r"`([^`]+)`\s*(.*)", item)
                if m:
                    out.append(
                        f'            <li><span class="d">{html.escape(m.group(1))}</span>'
                        f"<span>{inline(m.group(2))}</span></li>"
                    )
                else:
                    out.append(f"            <li>{inline(item)}</li>")
            else:
                if not dans_liste:
                    out.append("        <ul>")
                    dans_liste = True
                out.append(f"          <li>{inline(item)}</li>")
            continue

        # paragraphe
        fermer_journal()
        fermer_liste()
        out.append(f"        <p>{inline(l.strip())}</p>")

    fermer_balise()
    out.append("  </main>")
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────
# Assemblage
# ─────────────────────────────────────────────────────────────

def date_longue(d):
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month]} {d.year}".upper()


def rendre_numero(num, modele, precedent=None, suivant=None):
    nav = []
    if suivant:
        nav.append(f'<a href="{SITE}/{suivant["slug"]}/">← n° {suivant["numero"]}</a>')
    nav.append(f'<a href="{SITE}/archive/">Tous les numéros</a>')
    if precedent:
        nav.append(f'<a href="{SITE}/{precedent["slug"]}/">n° {precedent["numero"]} →</a>')

    edition = ""
    if num.get("edition"):
        edition = f'<span class="edition">{html.escape(num["edition"])}</span>'

    return (
        modele
        .replace("{{TITRE_PAGE}}", f'{TITRE_SITE} #{num["numero"]} — {html.escape(num["titre"])}')
        .replace("{{NUMERO}}", num["numero"])
        .replace("{{DATE_LONGUE}}", date_longue(num["date_obj"]))
        .replace("{{DATE_ISO}}", num["date"])
        .replace("{{EDITION}}", edition)
        .replace("{{CHAPO}}", html.escape(num.get("chapo", "")))
        .replace("{{CORPS}}", rendre_corps(num["corps"]))
        .replace("{{NAV}}", " · ".join(nav))
        .replace("{{DESCRIPTION}}", html.escape(num.get("chapo", DESCRIPTION_SITE)))
        .replace("{{URL_CANONIQUE}}", f'{SITE}/{num["slug"]}/')
    )


def rendre_archive(numeros, modele):
    lignes = []
    for n in numeros:
        d = n["date_obj"]
        lignes.append(
            f'      <li><a href="{SITE}/{n["slug"]}/">'
            f'<span class="arch-num">#{n["numero"]}</span>'
            f'<span class="arch-titre">{html.escape(n["titre"])}</span>'
            f'<span class="arch-date">{d.day} {MOIS[d.month]} {d.year}</span>'
            f"</a></li>"
        )
    return (
        modele
        .replace("{{TITRE_PAGE}}", f"{TITRE_SITE} — archive")
        .replace("{{DESCRIPTION}}", html.escape(DESCRIPTION_SITE))
        .replace("{{URL_CANONIQUE}}", f"{SITE}/archive/")
        .replace("{{LISTE}}", "\n".join(lignes))
        .replace("{{COMPTE}}", str(len(numeros)))
    )


def rendre_flux(numeros):
    maj = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entrees = []
    for n in numeros[:20]:
        url = f'{SITE}/{n["slug"]}/'
        entrees.append(f"""  <entry>
    <title>#{n['numero']} — {html.escape(n['titre'])}</title>
    <link href="{url}"/>
    <id>{url}</id>
    <updated>{n['date']}T08:00:00Z</updated>
    <summary>{html.escape(n.get('chapo', ''))}</summary>
  </entry>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{TITRE_SITE}</title>
  <subtitle>{html.escape(DESCRIPTION_SITE)}</subtitle>
  <link href="{SITE}/flux.xml" rel="self"/>
  <link href="{SITE}/"/>
  <id>{SITE}/</id>
  <updated>{maj}</updated>
{chr(10).join(entrees)}
</feed>
"""


def rendre_llms(numeros):
    l = [f"# {TITRE_SITE}", "", f"> {DESCRIPTION_SITE}", "", "## Numéros", ""]
    for n in numeros:
        l.append(f'- [#{n["numero"]} — {n["titre"]}]({SITE}/{n["slug"]}/) — {n["date"]}')
    l += ["", "## Notes", "",
          "Veille assistée par IA, relue et validée par un humain.",
          "Les informations non confirmées sont signalées comme telles dans le texte."]
    return "\n".join(l) + "\n"


def main():
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)

    numeros = charger_numeros()
    if not numeros:
        print("Aucun numéro publiable.")
        return

    modele_num = (MODELES / "numero.html").read_text(encoding="utf-8")
    modele_arch = (MODELES / "archive.html").read_text(encoding="utf-8")

    for idx, n in enumerate(numeros):
        precedent = numeros[idx + 1] if idx + 1 < len(numeros) else None
        suivant = numeros[idx - 1] if idx > 0 else None
        page = rendre_numero(n, modele_num, precedent, suivant)
        dossier = PUBLIC / n["slug"]
        dossier.mkdir(parents=True, exist_ok=True)
        (dossier / "index.html").write_text(page, encoding="utf-8")
        print(f"  ✓ /{n['slug']}/")

    # racine = dernier numéro
    dernier = rendre_numero(numeros[0], modele_num,
                            numeros[1] if len(numeros) > 1 else None, None)
    (PUBLIC / "index.html").write_text(dernier, encoding="utf-8")

    (PUBLIC / "archive").mkdir(exist_ok=True)
    (PUBLIC / "archive" / "index.html").write_text(
        rendre_archive(numeros, modele_arch), encoding="utf-8")

    (PUBLIC / "flux.xml").write_text(rendre_flux(numeros), encoding="utf-8")
    (PUBLIC / "llms.txt").write_text(rendre_llms(numeros), encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/flux.xml\n", encoding="utf-8")

    print(f"\n{len(numeros)} numéro(s) · archive · flux.xml · llms.txt → public/")


if __name__ == "__main__":
    main()
