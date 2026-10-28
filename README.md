# ☕ Le Café Patrimoine

Newsletter patrimoniale quotidienne pour un étudiant de M2 Gestion de patrimoine. Claude la rédige à partir de recherches web faites le matin même et l'envoie à 9h00 heure de Paris.

## Fonctionnement

- Une **routine Claude** (<https://claude.ai/code/routines>) se lance chaque jour à 6h30 UTC, soit 7h30 en hiver et 8h30 en été à Paris. Elle tourne sur l'abonnement Claude du propriétaire, sans aucun coût supplémentaire.
- La routine télécharge trois fichiers de ce dépôt : `routine/procedure.md`, `routine/outils.py` et `prompts/newsletter.md`. Elle cherche l'actualité, rédige la newsletter et vérifie les 9 sections. Elle attend ensuite 9h00 et envoie l'email avec le connecteur Gmail du propriétaire.
- Les newsletters envoyées restent dans la boîte « Envoyés » de Gmail. Chaque matin, la routine y relit les sujets de Focus des 30 derniers jours pour ne pas les répéter.

## Modifier

- **Contenu ou ton** : modifie `prompts/newsletter.md`. La modification est prise en compte dès le lendemain, une fois commitée.
- **Destinataires, nom, modèle ou horaire** : modifie la routine sur <https://claude.ai/code/routines>.

## Dépannage

- **Aucun email** : ouvre la routine sur <https://claude.ai/code/routines> et lis le journal de la dernière exécution.
- **« Pas de newsletter ce matin »** : la raison est indiquée dans l'email. Relance la routine avec **Run now**.
- **Connecteur Gmail déconnecté** : reconnecte-le sur <https://claude.ai/customize/connectors>.
- **Quota de l'abonnement atteint** : la routine échoue ce jour-là et repart normalement le lendemain.
