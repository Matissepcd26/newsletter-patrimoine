# Procédure quotidienne « Le Café Patrimoine »

Tu travailles seul : personne ne peut te répondre. Ne pose aucune question. Les valeurs NOM, DESTINATAIRES et TEST sont données dans le message de la routine. Tu travailles à la racine de ce dépôt.

1. Calcule les variables de date à l'heure de Paris : `python3 routine/outils.py variables`.
2. Sujets récents : avec l'outil Gmail `search_threads`, cherche `in:sent subject:"NOM" newer_than:30d`. Dans chaque extrait, relève le texte qui suit « Focus M2 du jour : ». FOCUS_RECENTS = ces sujets séparés par « ; ». Si la recherche échoue ou ne trouve rien, FOCUS_RECENTS = « aucun » et continue.
3. Lis `prompts/newsletter.md`. Remplace {{DATE}}, {{JOUR}} et {{FENETRE}} par les valeurs de l'étape 1, {{FOCUS_RECENTS}} par la liste de l'étape 2 et {{NOM_NEWSLETTER}} par NOM. Exécute ensuite ces consignes à la lettre, comme ton message de départ : recherches avec WebSearch et WebFetch, puis rédaction complète. Ne déduis jamais la date toi-même.
4. Écris le contenu de la balise `<newsletter_html>` dans /tmp/fragment.html. Retiens OBJET, le contenu de `<objet>`, et FOCUS, celui de `<focus_sujet>`.
5. Contrôle : `python3 routine/outils.py gabarit "NOM" "OBJET" "FOCUS"`. Si des lignes MANQUE=… s'affichent, complète la newsletter une seule fois, réécris /tmp/fragment.html et relance le contrôle. Si MOTS sort de 2 200 à 2 800, note-le dans ton bilan, sans rien changer.
6. Si TEST = oui, n'envoie rien : passe directement au bilan (étape 10).
7. Attends 09:00 heure de Paris. Répète cette commande jusqu'à ce qu'elle affiche 09:00 ou plus. Si 9h00 est déjà passée, continue tout de suite.
   ```
   for i in $(seq 16); do [ "$(TZ=Europe/Paris date +%H%M)" -ge 0900 ] && break; sleep 30; done; TZ=Europe/Paris date +%H:%M
   ```
8. Envoie avec l'outil Gmail `send_message` : `to` = DESTINATAIRES, `subject` = OBJET, `htmlBody` = contenu exact de /tmp/email.html, `body` = contenu exact de /tmp/email.txt.
9. En cas d'échec définitif de la rédaction ou du contrôle, envoie à DESTINATAIRES un email d'objet « Pas de newsletter ce matin », dont le corps dit « Pas de newsletter ce matin. Raison : » suivi de la raison en une phrase.
10. Termine par un bilan en quatre lignes : recherches web, pages lues, MOTS et lignes MANQUE, objet envoyé ou raison de l'échec.
