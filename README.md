# ☕ Le Café Patrimoine

Newsletter patrimoniale quotidienne pour un étudiant de M2 Gestion de patrimoine. Claude la rédige à partir de recherches web faites le matin même et l'envoie à 9h00 heure de Paris.

## Fonctionnement

- Une **routine Claude** (<https://claude.ai/code/routines>) se lance chaque jour à 7h25 heure de Paris, toute l'année. Elle tourne sur l'abonnement Claude du propriétaire, sans aucun coût supplémentaire.
- La routine travaille sur une copie de ce dépôt et suit `routine/procedure.md`. Elle cherche l'actualité, rédige la newsletter et vérifie les 9 sections. Elle attend ensuite 9h00 et envoie l'email avec le connecteur Gmail du propriétaire.
- Les newsletters envoyées restent dans la boîte « Envoyés » de Gmail. Chaque matin, la routine y relit les sujets de Focus des 30 derniers jours pour ne pas les répéter.

## Archives

Toutes les newsletters et leurs fiches Focus, classées par thème et consultables avec une recherche : <https://le-coffre-patrimoine.vercel.app> (relais Vercel de GitHub Pages). Après chaque envoi, la routine les ajoute sur la branche `claude/archives`, publiée par GitHub Pages.

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
