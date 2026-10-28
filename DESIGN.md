# Le Coffre : direction artistique

**Idée** : la salle des coffres d'une banque privée. Chaque édition du Café Patrimoine est rangée comme un dépôt : on ouvre le coffre avec sa clé, on consulte les fiches, et chaque chiffre est accompagné de sa preuve.

## Principes
- **Confiance d'abord** : chaque édition affiche ses sources, l'extrait exact qui justifie chaque chiffre et les contrôles passés.
- **Registre** : chiffres en Geist Mono à chasse fixe, filets fins, densité modérée.
- **Cadran de coffre** : anneaux concentriques or en CSS (`repeating-radial-gradient`) sur les seuls panneaux encre (entrée, fiche du jour). Aucune image décorative.
- **Contraste maximal** : encre presque noire sur blanc, ou l'inverse en mode sombre. Les actions principales et l'onglet actif sont en encre pleine.
- **Un seul signal** : l'or, réservé aux repères (thème du jour, aiguille du cadran, jours d'édition, liens).

## Système
- Couleurs : neutres zinc (`--bg`, `--surface`, `--line`), encre (`--primary`, `--vault`), or (`--signal` sur fond sombre, `--accent` pour le texte). Thème automatique, clair ou sombre, au choix dans la barre latérale.
- Barre latérale : rail de 72 px qui s'ouvre à 256 px au survol ou au clavier ; le contenu se décale au lieu d'être recouvert.
- Typographie : Geist (texte et titres), Geist Mono (chiffres, dates).
- Rayons : cartes 12 px, champs 10 px, boutons et filtres en pilule.
- Mouvement : un fondu de 0,35 s à l'arrivée d'une vue, désactivé si le système demande moins d'animations.

## Accès
La clé d'accès est vérifiée par son empreinte SHA-256 dans `app.js`. Le prénom et l'email restent dans le navigateur. C'est une porte personnelle, pas une protection : le dépôt et le site sont publics.
