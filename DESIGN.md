# Le Coffre : direction artistique

**Idée** : la salle des coffres d'une banque privée. Chaque édition du Café Patrimoine est rangée comme un dépôt : on ouvre le coffre avec sa clé, on consulte les fiches, et chaque chiffre est accompagné de sa preuve.

## Principes
- **Confiance d'abord** : chaque édition affiche ses sources, l'extrait exact qui justifie chaque chiffre et les contrôles passés.
- **Registre** : chiffres en Geist Mono à chasse fixe, filets fins, densité modérée.
- **Cadran de coffre** : anneaux concentriques en CSS (`repeating-radial-gradient`) sur les seuls panneaux verts (entrée, fiche du jour). Aucune image décorative.
- **Une seule couleur d'accent** : l'ambre, réservée aux actions et aux repères.

## Système
- Couleurs : vert forêt (`--vault`), blanc os (`--bg`), ambre (`--accent`), en mode clair et sombre automatique.
- Typographie : Geist (texte et titres), Geist Mono (chiffres, dates).
- Rayons : cartes 14 px, champs 10 px, boutons et filtres en pilule.
- Mouvement : un fondu de 0,35 s à l'arrivée d'une vue, désactivé si le système demande moins d'animations.

## Accès
La clé d'accès est vérifiée par son empreinte SHA-256 dans `app.js`. Le prénom et l'email restent dans le navigateur. C'est une porte personnelle, pas une protection : le dépôt et le site sont publics.
