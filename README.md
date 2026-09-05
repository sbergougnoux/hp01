# H0RS-P1STE

Veille hebdomadaire — IA agentique, fournisseurs de modèles, gateways,
intégration d'entreprise.

Publié sur https://newsletter.offro4d.ai

## Structure

```
wrangler.jsonc           config Cloudflare (sert public/)
contenu/numeros/NNN.md   source de vérité d'un numéro
contenu/inbox.md         liens collectés à la volée
contenu/pages/*.md       pages fixes (contact, etc.)
config/agenda.md         événements de la page Agenda
interne/notes/NNN.md     notes internes — NON publiées
modeles/                 templates HTML
config/sources.yaml      registre des sources de veille
scripts/build.py         génération du site
public/                  sortie générée, servie par Cloudflare
```

## Ajouter une page

Créer `contenu/pages/mapage.md` avec un frontmatter :

```yaml
---
titre: Ma page
slug: mapage
sous_titre: Phrase affichée sous le titre.
---
```

Elle sera générée dans `public/mapage/`. Pour l'ajouter au menu, éditer
le bloc `nav.menu` dans les trois fichiers de `modeles/` et la liste
`ONGLETS` de `scripts/build.py`.

## Ajouter un événement à l'agenda

Une ligne dans `config/agenda.md` :

```
- 2026-10-15 | API Days Paris | Paris | salon | https://example.com
```

Format : `date | intitulé | lieu | type | url`. La date accepte
`AAAA-MM-JJ` ou `AAAA-MM-JJ..AAAA-MM-JJ`. Le basculement vers
« Déjà passé » est automatique — mais il n'a lieu qu'au prochain build,
puisque le site est statique.

## Générer le site

```bash
python3 scripts/build.py
```

Aucune dépendance externe. Le contenu de `public/` est commité :
Cloudflare sert le dossier sans étape de build côté serveur.

## Déploiement

Cloudflare Workers, configuré par `wrangler.jsonc` (`assets.directory`
pointe sur `./public/`). Aucune commande de build côté Cloudflare : le
HTML est généré en local et commité. Chaque push sur `main` déclenche
le déploiement.

## Publier un numéro

1. L'agent écrit `contenu/numeros/NNN.md` sur une branche `draft/NNN`
   avec `statut: brouillon`.
2. Relecture et corrections.
3. Passer `statut: publie`, lancer le build, committer `public/`.
4. Fusionner sur `main` — le merge vaut approbation éditoriale.

**L'agent n'écrit jamais sur `main`.** Le seul geste qui publie est humain :
c'est ce qui rend vraie la mention « relue et validée par un humain », et ce
qui fait tenir l'exception de responsabilité éditoriale de l'article 50 de
l'AI Act.

## Frontmatter d'un numéro

```yaml
numero: "002"
titre: "Titre du numéro"
edition: "Mention optionnelle sous le titre"
date: 2026-09-04
chapo: "Une phrase de présentation."
statut: brouillon   # brouillon | publie
```

Seuls les numéros en `statut: publie` sont générés.
