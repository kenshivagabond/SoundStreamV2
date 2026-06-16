# 🔉 SoundStream

# Livrable pour les évaluations des Compétences :
## Compétence 2 :  
### livrable compétence 2 :  
[livrable compétence 2](00-Documents/rapport_compétence_2-1.pdf)  
## Compétence 4 :
### livrable compétences 4 :  
[livrable compétences 4](00-Documents/Compte_rendu_compétence_4%20(1).pdf)  
## Compétence 5 :  
### Synthèse des questions pour le receuil de besoin :  
[Synthèse des questions pour le receuil de besoin](00-Documents/Synthèse%20des%20questions%20à%20poser%20à%20Mr.pdf)  
### User story :  
[User story](00-Documents/Besoin_Utilisateurs.pdf)  
### Cahier des charges :  
[Cahier des charges](00-Documents/Cahier_des_ChargesV1.0.pdf)  
### Maquette :  
[Maquette](00-Documents/Screenshots-Maquette/V1/)   
### Fiche de route :  
[Fiche de route](00-Documents/Fiche_de_route.xlsx)  
[RACI](00-Documents/RACI.pdf)   
### Feuille de temps :  
[Feuille de temps](00-Documents/Feuille_de_temps_Neptune_A%20.pdf)  
### Paragraphe d'analyse du déroulement du projet :  
Pour ce qui est de la méthodologie de la gestion de ce projet, nous avons procédé comme cela : on a tout d’abord recueilli les besoins du client et on les a bien définis en les traduisant en  users stories. Puis nous avons créé le cahier des charges afin de cadrer  et  transformer les users stories en réelles exigences.Puis nous sommes passés à la planification des tâches, via une feuille de route qui nous a permis de connaître qui a fait quoi au sein du projet. Les obstacles étaient nombreux, nous avons eu du mal à bien planifier nos tâches car avant de commencer à coder le manière de procéder était très abstraite, mais à force de coder nous avons réussi à gagner en clarté sur l'avancée du projet. De plus, nous estimons avoir commencé la partie programmation du projet avec un peu de retard, ce qui nous  a donné un peu de stress et quelques nuits blanches à la fin du projet. Ainsi, pour conclure, nous estimons avoir bien conduit le projet malgré quelques obstacles sur la planification et la gestion du temps. 
## Compétence 6 :
### Compte-rendu :  
[Compte-rendu](00-Documents/Compte_rendu_compétence_6.pdf)  

# Livrable pour les évaluations des Compétences (S4) :


### Comment lancer l'application :
Il est nécessaire d'utiliser un environnement virtuel Python pour isoler les dépendances.

```bash
python3 -m venv env

# Windows
.\env\Scripts\activate

# macOS / Linux
source env/bin/activate

pip install -r requirements.txt

# Dans le répertoire SoundStream/Code
python3 main.py

```
Puis mettre l'URL http://127.0.0.1:8000/ dan votre navigateur.

### Qu'est ce que SoundStream
SoundStream est un projet que nous sommes en train de réaliser dans le cadre de la SAÉ S301 (SAÉ = projet évalué qui regroupe un ensemble de compétances afin de pouvoir appliquer les principes théoriques vus en cours). Elle est réalisée en groupe et consiste en le développement d'une application web complète.


### 🧑‍💻 Développeurs (V1)
| Participants      | Mail de contact                       | Discord               |
| ----------------- | ------------------------------------- | -----------           |
| HEURTAUX Romain   | heurtaux.romain@gmail.com             | romain_hrtx           |
| SY Aboubakry      | aboubakry.sy@edu.univ-paris13.fr      | -                     |
| CASSEL Kadir      | kadir.cassel06@gmail.com              | -                     |
| COLLEN Tristan    | tristan.collen@edu.univ-paris13.fr    | -                     |
| ALJANE Saif-Eddine| saifeddinealjane@gmail.com            | -                     |
- Groupe Neptune A

### 🧑‍💻 Développeurs (V2)
| Participants      | Mail de contact                       | Discord               |
| ----------------- | ------------------------------------- | -----------           |
| HEURTAUX Romain   | heurtaux.romain@gmail.com             | romain_hrtx           |
| FILLONNEAU Kenzo  | kenzo.fillonneau@edu.univ-paris13.fr  | -                     |
| SEBBAH Sofiane    | sofianesbh6@gmail.com                 | -                     |
| LEMEST Enzo       |                                       | -                     |
| Lucas             |                                       | -                     |
- Groupe Neptune A
### 🖊️ Descriptif du projet

Dans beaucoup d’organisations (entreprises, collectivités, gares, campus…), il faut assurer une diffusion musicale continue, avec insertion de messages publicitaires et possibilité de lancer des messages urgents. L’enjeu est de garantir la continuité de service : même en cas de coupure réseau, il doit toujours y avoir de la musique qui joue. La supervision permet en plus de vérifier que chaque lecteur est bien en fonctionnement et que ses playlists de secours sont correctement synchronisées.

L’idée serait de mettre en place un système de supervision qui permette :
- de suivre l’état des lecteurs
- de mettre à jour en central la playlist locale et de la synchroniser automatiquement sur les lecteurs
- de vérifier que la playlist locale de secours est bien à jour
- de consigner les messages diffusés (musique, publicité, urgent)
- et de déclencher des alertes en cas de problème (lecteur KO, playlist obsolète,absence de diffusion).

Une version V2 à été proposer en rigueur des problémes observer dans la version Vanilla avec une architecture réseaux totalement revue

Les étudiants développeraient la solution pour un pilote :
1. Deux lecteurs test (site principal + 2 sites distants)
2. Tableau de bord simple (état, synchro, “now playing”)
3. Stocker l’historique.
4. Scénarios de test : coupure réseau, coupure électrique, diffusion d’un message urgent, respect du planning des publicités.


### 🧋 Autres Sources
- [🐈‍⬛ Le Github](https://github.com/hrtxr/SoundStream)
- [🔗 Le Moodle](https://moodle.univ-spn.fr/course/view.php?id=7746)
