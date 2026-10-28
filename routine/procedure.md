# Procédure quotidienne « Le Café Patrimoine »

Tu travailles seul : personne ne peut te répondre. Ne pose aucune question. Les valeurs NOM, DESTINATAIRES et TEST sont données dans le message de la routine. Tu travailles à la racine de ce dépôt. La qualité attendue est notée selon `eval/grille.md` : vise 100/100, et surtout zéro erreur factuelle.

1. **Dates.** `python3 routine/outils.py variables`. Ces valeurs font foi : ne déduis jamais la date toi-même.
2. **Focus récents.** Avec l'outil Gmail `search_threads`, cherche `in:sent to:(DESTINATAIRES) subject:"NOM" newer_than:30d`. Dans chaque extrait, relève le texte qui suit « Focus M2 du jour : ». FOCUS_RECENTS = ces sujets séparés par « ; ». Si la recherche échoue ou ne trouve rien, FOCUS_RECENTS = « aucun ».
3. **Consignes.** Lis `prompts/newsletter.md`. Remplace {{DATE}}, {{JOUR}}, {{FENETRE}}, {{FOCUS_RECENTS}} et {{NOM_NEWSLETTER}}. Ces consignes sont ton cahier des charges, à suivre à la lettre.
4. **Recherche, selon ce protocole.**
   - **Marchés** : lance `python3 routine/marches.py`. Il donne pour chaque actif la dernière clôture, la variation et la date de clôture, d'après Yahoo Finance et CNBC : ces chiffres font foi. Arrondis les taux à deux décimales. Vérifie chaque valeur par une recherche (par exemple « CAC 40 clôture 28 octobre 2026 »). Si l'écart dépasse 0,3 %, privilégie la source la plus proche de l'émetteur (Euronext, Banque de France, BCE, ICE, CME) et note-le dans /tmp/faits.md. Si le script affiche « non disponible », cherche le chiffre en exigeant deux sources concordantes ; à défaut, écris « non disponible ce matin ». Le week-end, le script donne la variation sur la semaine. Pour l'OAT et le Bund, cherche alors la variation hebdomadaire en points de base. Cite « Yahoo Finance — Historique des cours » et « CNBC — Rendements souverains » dans les Sources, avec les liens affichés. Tes recherches servent surtout à expliquer chaque mouvement.
   - **Rubriques** : au moins deux recherches par rubrique, dont une qui vise une source primaire avec `site:` (ecb.europa.eu, banque-france.fr, insee.fr, economie.gouv.fr, legifrance.gouv.fr, bofip.impots.gouv.fr, amf-france.org, service-public.fr, assemblee-nationale.fr, federalreserve.gov).
   - **Focus** : vérifie chaque article de loi, taux, seuil et abattement sur Légifrance, le BOFiP ou service-public.fr. Note l'article exact et sa version en vigueur.
   - **Pages** : essaie WebFetch sur les pages clés. Si le réseau refuse un site, ne le réessaie pas et appuie-toi sur les extraits de recherche.
   - **Journal des faits** : consigne chaque fait retenu dans /tmp/faits.md, une ligne par fait : affirmation | valeur | média | titre | URL | date de publication. Rien n'entre dans la newsletter sans sa ligne.
5. **Calculs du Focus.** Fais chaque opération de l'exemple chiffré avec python3, en affichant les étapes, et recopie exactement les résultats.
6. **Rédaction.** Écris le contenu de `<newsletter_html>` dans /tmp/fragment.html. Retiens OBJET (`<objet>`) et FOCUS (`<focus_sujet>`).
7. **Relecture factuelle**, ligne à ligne :
   - chaque chiffre, date, nom et décision du fragment correspond à une ligne de /tmp/faits.md, avec la même valeur ; sinon corrige-le ou supprime-le ;
   - chaque source de la rubrique Sources a servi, et chaque fait sourcé y figure ;
   - aucune actualité ne sort de la fenêtre ;
   - chaque mesure fiscale indique son stade (en vigueur, voté, projet, amendement) ;
   - les expressions de temps (« hier », « ce matin », « cette nuit ») restent justes pour un lecteur qui ouvre l'email à 9h00 le jour indiqué.
8. **Contrôle automatique.** `python3 routine/outils.py gabarit "NOM" "OBJET" "FOCUS"`, puis `python3 eval/evaluer.py /tmp/email.html "OBJET"`. Corrige chaque écart signalé (longueur des sections, formats, objet), réécris le fragment et relance les deux commandes. Vise total_auto = 23, avec 3 corrections au maximum.
9. **Si TEST = oui** : envoie tout de suite (étape 11), avec l'objet « [TEST] OBJET ».
10. **Sinon, attends 09:00 heure de Paris.** Répète la commande ci-dessous jusqu'à ce qu'elle affiche 09:00 ou plus. Si 9h00 est déjà passée, continue tout de suite.
   ```
   for i in $(seq 16); do [ "$(TZ=Europe/Paris date +%H%M)" -ge 0900 ] && break; sleep 30; done; TZ=Europe/Paris date +%H:%M
   ```
11. **Envoi** avec l'outil Gmail `send_message` : `to` = DESTINATAIRES, `subject` = OBJET, `htmlBody` = contenu exact de /tmp/email.html, `body` = contenu exact de /tmp/email.txt.
12. **Échec.** Si la rédaction ou le contrôle échoue définitivement, envoie à DESTINATAIRES un email d'objet « Pas de newsletter ce matin », dont le corps dit « Pas de newsletter ce matin. Raison : » suivi de la raison en une phrase.
13. **Bilan**, en cinq lignes : recherches web, pages lues, nombre de lignes de /tmp/faits.md, total_auto final, objet envoyé ou raison de l'échec.
