# H0RS-P1STE

Veille hebdomadaire — IA agentique, fournisseurs de modèles, gateways,
intégration d'entreprise.

Publié sur https://newsletter.offro4d.ai

## Structure

```
contenu/numeros/NNN.md   source de vérité d'un numéro
contenu/inbox.md         liens collectés à la volée
interne/notes/NNN.md     notes internes — NON publiées
modeles/                 templates HTML
config/sources.yaml      registre des sources de veille
scripts/build.py         génération du site
public/                  sortie générée, servie par Cloudflare Pages
```

## Générer le site

```bash
python3 scripts/build.py
```

Aucune dépendance externe. Le contenu de `public/` est commité :
Cloudflare Pages sert le dossier sans étape de build côté serveur.

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
