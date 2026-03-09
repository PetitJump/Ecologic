# Nature du code et usage de l'IA

## Degré de création originale

Le projet Naturalia est entièrement original. L'idée, la conception du modèle biologique, l'architecture Flask, le système de succès et l'interface graphique ont été pensés et réalisés par l'équipe.

Les modèles mathématiques utilisés (croissance logistique, modèle prédateur-proie inspiré de Lotka-Volterra) sont des concepts académiques standards, librement documentés, que nous avons adaptés à notre simulation discrète par années.

## Sources externes citées

- **Flask** (framework web Python) — https://flask.palletsprojects.com/
- **Modèle logistique** (croissance avec capacité de charge) — cours de mathématiques et ressources Wikipédia
- **Polices Google Fonts** : Playfair Display, Lato — https://fonts.google.com/
- Aucune bibliothèque externe de simulation ou de visualisation n'a été utilisée : le graphique canvas est codé en JavaScript pur.

## Utilisation de l'intelligence artificielle

Nous avons utilisé Claude (Anthropic) comme assistant tout au long du développement, principalement pour :

- **Débogage** : identifier et corriger des bugs (ex. la fonction `random_repro` qui écrasait les paramètres, le broutage des cerfs non implémenté)
- **Calibrage de la simulation** : tester différentes valeurs de paramètres biologiques et analyser les résultats de simulations en boucle
- **Aide à la rédaction HTML/CSS/JS** : mise en forme de l'interface, graphique canvas double axe, animations

L'IA a servi d'outil d'assistance technique. Tous les choix de conception (modèle biologique, architecture, fonctionnalités, paramètres) ont été décidés par l'équipe. Nous sommes en mesure d'expliquer et de justifier chaque partie du code.

L'usage de l'IA a été limité aux aspects techniques et de débogage, jamais à la génération automatique de fonctionnalités complètes sans compréhension de notre part.
