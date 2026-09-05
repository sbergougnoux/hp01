# H0RS-P1STE — plan de démarrage

Document de cadrage à valider avant lancement.
État au 28 août 2026.

---

## Phase 0 — Décisions à trancher

Rien ne démarre avant ces arbitrages. Ce sont des choix, pas des tâches.

| # | Décision | Options | Recommandation |
|---|---|---|---|
| D1 | Nom retenu | H0RS-P1STE / autre | à confirmer, le nom conditionne le domaine |
| D2 | Domaine | hp01.io / hp01.fr / sous-domaine | `.fr` si le budget prime, `.io` si média autonome |
| D3 | Cadence | hebdo / bi-mensuelle | hebdo, jour fixe — la régularité prime sur le volume |
| D4 | Jour de parution | — | mardi ou jeudi matin ; éviter lundi et vendredi |
| D5 | Signature éditoriale | anonyme / Fondaxion / nom propre | à revoir après 3 numéros (voir note AI Act) |
| D6 | Hébergement | Cloudflare / Netlify | Cloudflare (bande passante gratuite, Workers) |
| D7 | Périmètre des balises | 6 balises actuelles | figer maintenant, réviser au numéro 010 |

---

## Phase 1 — Fondations

Objectif : un dépôt et une adresse. Aucune automatisation encore.

1. Réserver le domaine (D2) et le rattacher à l'hébergeur (D6).
2. Créer le dépôt Git, privé au départ.
   Structure proposée :
   ```
   /contenu/numeros/001.md      ← source de vérité
   /contenu/inbox.md            ← liens collectés à la volée
   /interne/notes/001.md        ← notes internes (jamais publiées)
   /modeles/numero.html         ← template
   /config/sources.yaml         ← registre des sources
   /scripts/                    ← collecte, build
   /public/                     ← sortie générée
   ```
3. Décider où vivent les notes internes : dossier exclu du build, ou dépôt séparé.
   Le dépôt séparé est plus sûr qu'une règle d'exclusion.
4. Convertir le numéro 001 en markdown et vérifier que le template le régénère à l'identique.

**Livrable :** le numéro 001 en ligne, publié à la main. Rien d'automatique.

---

## Phase 2 — Registre de sources

Objectif : remplacer la recherche à l'aveugle par des sources tenues.

5. Vérifier une par une les URL de flux marquées `?` dans `sources.yaml`.
   Tester chaque flux, noter celles qui n'en ont pas.
6. Pour les sources sans flux : décider entre scraping léger et recherche ciblée.
   Ne pas scraper ce qui n'en vaut pas la peine.
7. Compléter les entrées `?` (Gravitee, Boomi, MuleSoft, LeMagIT, etc.).
8. Ajouter les flux `releases.atom` des dépôts GitHub suivis.
9. Mettre en place `inbox.md` : le fichier où tu colles une URL en passant.

**Livrable :** un `sources.yaml` dont chaque entrée a été testée.

---

## Phase 3 — Agent de collecte

Objectif : produire un brouillon exploitable, pas un numéro fini.

10. Script de collecte : parcourt le registre, récupère les nouveautés depuis
    la dernière passe, dédoublonne, écrit un fichier de matière brute.
11. Ajouter la recherche ouverte en complément (requêtes du registre).
12. Filtrage : écarter la liste noire, remonter aux sources primaires.
13. Rapport de passe : ce qui a été trouvé, ce qui a échoué, quelles sources
    nouvelles sont proposées à l'ajout.

**Livrable :** un fichier de matière brute par semaine, lisible tel quel.

---

## Phase 4 — Rédaction

Objectif : transformer la matière en brouillon de numéro.

14. Écrire le prompt de rédaction. Il doit contenir explicitement :
    - la règle de vocabulaire (français d'abord, anglais entre parenthèses,
      pas de traduction quand l'usage est anglais)
    - la règle d'édito (commenter le marché, jamais la situation du lecteur)
    - le signalement obligatoire des informations non confirmées
    - le plafond de 2 articles par balise, le reste en format timeline
    - les critères anti-écriture générique : varier les attaques, assumer un
      jugement, signaler les chiffres d'éditeur non vérifiés
15. Double sortie : le numéro public et la note interne, en deux fichiers.
16. Vérification automatique avant livraison : dates, montants, disponibilité
    des liens.

**Livrable :** brouillon poussé sur une branche `draft/NNN`.

---

## Phase 5 — Chaîne éditoriale

Objectif : garantir techniquement qu'aucun numéro ne part sans relecture.

17. Interdire à l'agent d'écrire sur la branche principale.
18. Notification quand le brouillon est prêt.
19. Choisir l'outil de relecture : Claude Code pour le fond, CMS ou Pull
    Request pour la passe finale.
20. Le merge vaut approbation : nominatif, horodaté, tracé.

**Livrable :** un chemin de validation où le seul geste qui publie est le tien.

---

## Phase 6 — Publication

21. Build markdown → HTML depuis le template.
22. Page d'archive avec une URL par numéro.
23. Flux RSS/Atom.
24. `llms.txt` à la racine.
25. Déploiement automatique au merge.

**Livrable :** le site à jour sans intervention manuelle après validation.

---

## Phase 7 — Diffusion

26. Déclinaison email du template (styles en ligne, mise en page en tableaux —
    le CSS actuel ne passera pas les clients mail).
27. Choix de l'outil d'emailing et import de la liste.
28. Newsletter LinkedIn en relais d'acquisition.
29. Optionnel : rendu terminal via `curl`.

---

## Phase 8 — Serveur MCP

À faire après trois ou quatre numéros, quand l'archive a du contenu.

30. Worker exposant l'archive : recherche par balise, par période, par acteur.
31. Documenter le point d'accès sur le site.
32. En faire un sujet de contenu — c'est la démonstration de la thèse.

---

## Ce que le plan ne couvre pas volontairement

- **La veille humaine.** Les trois meilleurs sujets du numéro 001 venaient de
  toi. Aucune automatisation ne remplacera les signaux issus des échanges
  clients et des contacts éditeurs.
- **La ligne éditoriale dans la durée.** Elle se décidera en écrivant, pas en
  cadrant.
- **La monétisation.** Hors sujet tant que la cadence n'est pas tenue.

---

## Point de vigilance récurrent

La mention « relue et validée par un humain » n'est vraie que tant que la
relecture existe. Si un jour la publication devient automatique, la mention
doit changer et l'exception éditoriale de l'article 50 tombe.

---

## Ordre de priorité suggéré

Phases 1 et 2 d'abord : sans registre vérifié, l'agent produira du bruit.
Phases 3 à 5 ensuite, en acceptant un premier agent médiocre — il s'améliore
en corrigeant ses sorties, pas en le peaufinant avant le premier essai.
Phases 6 à 8 quand trois numéros seront sortis à l'heure.
