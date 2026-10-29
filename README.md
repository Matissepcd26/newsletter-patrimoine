# ◆ Le Coffre

Newsletter patrimoniale quotidienne pour un étudiant de M2 Gestion de patrimoine. Claude la rédige à partir de recherches web faites le matin même et l'envoie à 9h00 heure de Paris.

## Fonctionnement

- Une **routine Claude** (<https://claude.ai/code/routines>) se lance chaque jour à 6 h 30 heure de Paris (envoi à l'heure choisie par Mathéo, 8 h à 9 h 30), toute l'année. Elle tourne sur l'abonnement Claude du propriétaire, sans aucun coût supplémentaire.
- La routine travaille sur une copie de ce dépôt et suit `routine/procedure.md`. Elle cherche l'actualité, rédige la newsletter et vérifie les 9 sections. Elle attend ensuite 9h00 et envoie l'email avec le connecteur Gmail du propriétaire.
- Les newsletters envoyées restent dans la boîte « Envoyés » de Gmail. Chaque matin, la routine y relit les sujets de Focus des 30 derniers jours pour ne pas les répéter.

## Archives

Toutes les newsletters et leurs fiches Focus, classées par thème et consultables avec une recherche : <https://le-coffre-patrimoine.vercel.app> (relais Vercel de GitHub Pages). Après chaque envoi, la routine les ajoute sur la branche `claude/archives`, publiée par GitHub Pages.

## Modèle du mail

Mathéo règle l'esthétique (couleurs, police, taille, largeur, titres) et le contenu (rubriques masquées, deux rubriques ajoutées, sujets à suivre, note) sur la page « Modèle du mail » du dashboard, avec la clé d'accès. Le modèle est enregistré par `api/modele` (fonction Vercel, stockage Vercel Blob `coffre-modele`, 20 versions gardées). Chaque matin, `routine/outils.py modele` le lit et l'applique : le gabarit prend le style, la rédaction suit les rubriques, `eval/evaluer.py` adapte ses contrôles. Le réseau de la routine n'atteint pas le dashboard : la tâche GitHub `.github/workflows/modele.yml` recopie donc le modèle chaque heure (à h 17) dans `config/modele.json`, que la routine lit dans son clone. Sans copie, elle garde le modèle d'origine.

## Surveillance

- La routine envoie une notification au propriétaire si l'envoi, l'archivage ou un contrôle échoue (étape 13 bis).
- `.github/workflows/veille.yml` vérifie vers 10 h 30 que l'édition du jour est archivée, sauf jour sans envoi ; sinon GitHub envoie un mail d'échec au propriétaire du dépôt.
- `.github/workflows/modele.yml` recopie chaque heure le modèle du dashboard dans `config/modele.json`.

## Réglages de Mathéo (page Modèle du mail)

Longueur (condensé, standard, complet), ordre et choix des rubriques, deux rubriques ajoutées, bloc L'essentiel, question d'examen (réponse sur le Coffre), bouton vers l'édition complète, en-tête, titres, marchés en tableau, espacement, encadrés, police, couleurs, jours et heure de réception, pause.

## Qualité

- `routine/marches.py` lit les 10 dernières clôtures de marché (Yahoo Finance, CNBC) avant toute recherche.
- `routine/outils.py chiffres` refuse tout chiffre de la newsletter absent du journal des faits. `routine/outils.py journal` refuse tout fait dont l'extrait cité ne contient pas la valeur.
- Avant l'envoi, un sous-agent neuf revérifie chaque fait, et `eval/evaluer.py` contrôle le cahier des charges.
- La note de référence est définie dans `eval/grille.md`, sur 100 points. Une routine « TEST » envoie des versions de test au propriétaire seulement, avec « [TEST] » dans l'objet.

## Modifier

- **Contenu ou ton** : modifie `prompts/newsletter.md`. La modification est prise en compte dès le lendemain, une fois commitée.
- **Destinataires, nom, modèle ou horaire** : modifie la routine sur <https://claude.ai/code/routines>.

## Dépannage

- **Aucun email** : ouvre la routine sur <https://claude.ai/code/routines> et lis le journal de la dernière exécution.
- **« Pas de newsletter ce matin »** : la raison est indiquée dans l'email. Relance la routine avec **Run now**.
- **Connecteur Gmail déconnecté** : reconnecte-le sur <https://claude.ai/customize/connectors>.
- **Quota de l'abonnement atteint** : la routine échoue ce jour-là et repart normalement le lendemain.
