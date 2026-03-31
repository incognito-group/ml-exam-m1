# Lien vidéo présentation : 
https://www.youtube.com/@Tsizehena
titre : Présentation Vidéo

# Installation : 
run : pip3 install -r requirements
      python3 app.py
      ouvrir le fichier /interface/home.html

# Question réponse :
Q1 — Analyse des coefficients

x_wins : les coefficients les plus élevés en valeur absolue sont souvent autour des cases centrales et des coins. Sur un plateau de tic-tac-toe, la case centrale (position 5) est en général la plus influente (accès à plus de lignes gagnantes), donc oui, elle apparaît souvent comme la plus importante.
is_draw : les coefficients forts sont sur les cases qui empêchent les lignes gagnantes directes, souvent la case centrale et les bords critiques.
Cohérence avec stratégie humaine : humain sait que centre et coins sont clés ; le modèle le reflète en attribuant fort poids à ces positions.

Q2 — Déséquilibre des classes

x_wins : généralement déséquilibré (plus de non-victoires que de victoires).
is_draw : aussi déséquilibré (les tirages sont moins fréquents que les parties décisives).
Métrique : privilégier F1 et AUC (ou précision/rappel) plutôt que accuracy. Accuracy peut être trompeuse sur classes déséquilibrées. F1 gère mieux le tradeoff entre faux positifs/negatifs ; AUC montre capacité à séparer.

Q3 — Comparaison des deux modèles

Meilleur score : souvent x_wins est plus facile et obtient meilleur AUC/F1 que is_draw.
Difficulté : is_draw plus difficile car dépend de situation finale et nombreuses positions valides/invalides, patterns plus diffus.
Erreurs fréquentes : positions où le jeu est déjà quasiment décidé par un coup à venir (double menace, force fork), ou positions proches de victoire de l’adversaire.

Q4 — Mode hybride

Comportement : mode hybride (IA + ML) tend à mieux éviter les pièges que mode pure IA-ML, car il combine règles de jeu et prédiction.
Observations qualitatives : le joueur hybride gagne en stabilité dans les transitions milieu-fin de jeu, réduit les coups risqués (fausses branches), et évite mieux les tours critiques (forks, blocages manqués).
