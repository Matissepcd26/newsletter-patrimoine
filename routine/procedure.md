# Procédure quotidienne « Le Café Patrimoine »

Tu travailles seul : personne ne peut te répondre. Ne pose aucune question. Les valeurs NOM et DESTINATAIRES sont données dans le message de la routine.

1. Prépare les fichiers et les variables de date, calculées à l'heure de Paris :
   ```
   cd /tmp && B=https://raw.githubusercontent.com/Matissepcd26/newsletter-patrimoine/main
   curl -fsSLO $B/routine/outils.py && curl -fsSL $B/prompts/newsletter.md -o /tmp/prompt.md
   python3 /tmp/outils.py variables
   ```
2. Sujets récents : avec l'outil Gmail `search_threads`, cherche `in:sent subject:"NOM" newer_than:30d`. Dans chaque extrait, relève le texte qui suit « Focus M2 du jour : ». FOCUS_RECENTS = ces sujets séparés par « ; », ou « aucun ».
3. Lis /tmp/prompt.md. Remplace {{DATE}}, {{JOUR}} et {{FENETRE}} par les valeurs de l'étape 1, {{FOCUS_RECENTS}} par la liste de l'étape 2 et {{NOM_NEWSLETTER}} par NOM. Exécute ensuite ces consignes à la lettre, comme ton message de départ : recherches avec WebSearch et WebFetch, puis rédaction complète. Ne déduis jamais la date toi-même.
4. Écris le contenu de la balise `<newsletter_html>` dans /tmp/fragment.html. Retiens OBJET, le contenu de `<objet>`, et FOCUS, celui de `<focus_sujet>`.
5. Contrôle : `python3 /tmp/outils.py gabarit "NOM" "OBJET" "FOCUS"`. Si des lignes MANQUE=… s'affichent, complète la newsletter une seule fois, réécris /tmp/fragment.html et relance le contrôle. Si MOTS sort de 2 200 à 2 800, note-le dans ton bilan, sans rien changer.
6. Attends 09:00 heure de Paris. Répète cette commande jusqu'à ce qu'elle affiche 09:00 ou plus. Si 9h00 est déjà passée, continue tout de suite.
   ```
   for i in $(seq 16); do [ "$(TZ=Europe/Paris date +%H%M)" -ge 0900 ] && break; sleep 30; done; TZ=Europe/Paris date +%H:%M
   ```
7. Envoie avec l'outil Gmail `send_message` : `to` = DESTINATAIRES, `subject` = OBJET, `htmlBody` = contenu exact de /tmp/email.html, `body` = contenu exact de /tmp/email.txt.
8. En cas d'échec définitif de la rédaction ou du contrôle, envoie à DESTINATAIRES un email d'objet « Pas de newsletter ce matin », dont le corps dit « Pas de newsletter ce matin. Raison : » suivi de la raison en une phrase.
9. Termine par un bilan en trois lignes : recherches web, pages lues, objet envoyé ou raison de l'échec.
