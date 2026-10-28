# Grille de notation — newsletter parfaite = 100/100

Objectif de la boucle : au moins 95/100 sur deux newsletters de test consécutives, sans aucune erreur factuelle.

## A. Exactitude factuelle — 40 points (vérificateur indépendant, recherche web)
- **A1 Marchés (15)** : les 10 actifs sont présents. Chaque niveau et chaque variation correspondent à la dernière clôture disponible, dont la date est indiquée. Retirer 1,5 point par chiffre faux et 0,5 par date de clôture absente ou ambiguë. Un « non disponible » vaut 0,5 de pénalité, une estimation déguisée 3.
- **A2 Autres faits (15)** : chaque chiffre, date, nom et décision se vérifie dans une source fiable. Retirer 3 points par erreur et 1 par imprécision trompeuse.
- **A3 Focus M2 (10)** : la référence légale est exacte et en vigueur, les taux, seuils et abattements sont à jour, et chaque étape du calcul est juste. Retirer 5 points par erreur de droit ou de calcul et 2 par imprécision.

## B. Sourçage et fraîcheur — 15 points (vérificateur)
- **B1 Sources (8)** : chaque affirmation chiffrée a une source listée, au format « Média — titre » avec un lien réel. Le dossier s'appuie sur des sources primaires (BCE, INSEE, Légifrance, BOFiP, AMF…). Aucune source n'est citée sans servir.
- **B2 Fenêtre (4)** : aucune actualité hors de la fenêtre du jour.
- **B3 Statut des textes (3)** : chaque mesure fiscale précise son stade (en vigueur, voté, projet, amendement).

## C. Cahier des charges — 25 points (`eval/evaluer.py`, automatique)
- **C1 (5)** : les 9 titres `<h2>` exacts, dans l'ordre.
- **C2 (8)** : 4 points pour un total de 2 300 à 2 600 mots hors Sources, et 4 points au prorata des sections dans leur fourchette.
- **C3 (4)** : aucun tableau, des listes seulement pour les marchés et les sources, exactement 10 lignes de marché.
- **C4 (2)** : la mention finale exacte.
- **C5 (2)** : un objet au format « ☕ NOM — jour date : titre », avec un titre de moins de 8 mots.
- **C6 (2)** : le Focus suit la rotation du jour et ne reprend aucun Focus des 30 derniers jours.
- **C7 (2)** : les formats imposés sont respectés (EUR/USD à 4 décimales, OAT et Bund en % et en pb, or en $/once, Brent en $/baril, Bitcoin en $).

## D. Rédaction — 15 points (vérificateur)
- **D1 (4)** : l'édito défend un avis tranché et argumenté, et chaque opinion est signalée (« Mon avis : », « À mon sens »).
- **D2 (4)** : le texte respecte le ton demandé (tutoiement, première personne, phrases courtes, humour sec et rare, rien de racoleur).
- **D3 (3)** : les sujets sensibles sont traités avec neutralité, chaque position est attribuée à son auteur, et l'avis porte uniquement sur l'impact de marché.
- **D4 (4)** : l'apport pédagogique M2 est réel (« ce que ça change » concret, piège classique pertinent).

## E. Fiabilité — 5 points (journal de la routine)
- Le mail part à 9h00 à 2 minutes près, sans échec ni relance inutile. Les Focus déjà traités sont bien exclus, et le rendu de l'email est correct.
