# Guide d'Utilisation des Scripts SoundStream

Ce document explique comment installer et utiliser les scripts de configuration pour le projet **SoundStreamV2**, que vous soyez sur **Linux** ou sur **macOS**.

Il existe deux rôles pour les machines dans ce projet :

- **Serveur** : La machine qui diffuse la musique et configure le réseau de diffusion multicast.
- **Client** : Les lecteurs qui reçoivent la musique et disposent d'un plan d'urgence (fallback local) en cas de coupure réseau.

Les scripts fonctionnent sur le même principe :

- L'argument `i` (install) permet d'installer les dépendances et initialiser la configuration.
- L'argument `x` (execute) permet de lancer les services pour la diffusion ou la réception.

---

## Utilisation sur Linux (Environnement de Production)

Les scripts originaux (`soundstream_server.sh` et `soundstream_client.sh`) ont été conçus pour des distributions Linux (notamment basées sur Arch Linux avec `pacman` et Debian/Ubuntu avec `apt`). Ils utilisent `systemd` pour les services et gèrent nativement les interfaces réseau virtuelles (VXLAN) requises pour le multicast.

### Prérequis

- Avoir les droits d'administrateur (`sudo`).

1. **Installation** (installe Tailscale, MPD, FFmpeg et configure le réseau) :

   ```bash
   cd Code
   sudo ./soundstream_server.sh i
   ```

2. **Exécution** (lance MPD et monte l'interface réseau multicast) :

   ```bash
   cd Code@
   ```bash
   cd Code
   sudo ./soundstream_client.sh x
   ```

---

## Utilisation sur macOS (Test Local & Interface Web)

Des scripts spécifiques ont été créés pour permettre de tester le projet sur un Mac sans générer d'erreurs liées à `systemd` ou `apt/pacman`.

### 1. Prérequis & Configuration du Système

- **Homebrew** doit être installé sur votre Mac (la commande `brew` doit être accessible).
- **NE PAS utiliser** `sudo` pour lancer ces scripts. Homebrew ne l'autorise pas pour des raisons de sécurité.

**Important : Configuration SSH**Pour que le serveur puisse envoyer de la musique aux clients (y compris à lui-même en test local), macOS doit autoriser le SSH silencieux. Vous devez configurer ceci une seule fois :

1. Allez dans **Réglages Système** &gt; **Général** &gt; **Partage**.
2. Cochez **Session à distance** (Remote Login).
3. Ouvrez un terminal et corrigez les permissions de votre dossier personnel pour que SSH accepte les clés (macOS bloque SSH si le dossier est lisible par d'autres) :

   ```bash
   chmod 755 ~
   ```
4. Générez et autorisez une clé SSH pour les tests locaux (validez avec la touche "Entrée" à chaque question) :

   ```bash
   ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
   cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

### 2. Le Serveur Principal (Interface Web & Envoi de Musique)

C'est l'interface qui permet de monitorer les boitiers et planifier les envois. Le système Python envoie les musiques via `rsync` et commande les lecteurs via `ssh`.

1. **Vider et initialiser la base de données (si besoin)** :

   ```bash
   python3 Utils/Seeder.py
   # Répondez True pour effacer la base, False pour tout insérer (ou choisissez manuellement Utilisateurs, Orgas, etc.)
   ```

2. **Démarrer l'Interface et le Planificateur (Serveur Python)** : Ouvrez un terminal, placez-vous dans le dossier `Code`, et lancez le serveur via l'environnement virtuel. C'est lui qui scanne les appareils Tailscale et synchronise la musique.

   ```bash
   cd Code
   ./venv/bin/python main.py
   ```

Accédez à l'interface de gestion via **http://127.0.0.1:8000/** dans votre navigateur.

1. *Pour arrêter le serveur : Appuyez sur* `Ctrl + C` *dans son terminal.*

### 3. Le Lecteur Client (Récepteur Audio Mac)

Pour tester si la réception et la lecture de musique marchent sur le Mac, il faut démarrer le module client.

1. **Installation** (installe les paquets via Homebrew, prépare les dossiers `~/audio` et config `~/.mpdconf`) : Ouvrez un *nouveau* terminal :

   ```bash
   cd Code
   ./soundstream_client_macos.sh i
   ```

2. **Exécution** (lance le lecteur `mpd` en tâche de fond et se met à l'écoute des ordres du serveur principal) :

   ```bash
   cd Code
   ./soundstream_client_macos.sh x
   ```

   *Note : Le terminal peut afficher "Aucune playlist locale trouvée", c'est normal, il se met simplement en attente des musiques envoyées par le serveur.*

---

## Arrêt et Statut des Services (Audio & Réseau)

Une fois les scripts d'exécution (`x`) lancés, les services audio tournent en tâche de fond. Voici comment vérifier leur état ou les arrêter.

### Sur Linux

**Pour le Serveur :**

- **Voir le statut :** `sudo systemctl status mpd`
- **Arrêter le serveur :** `sudo systemctl stop mpd`

**Pour le Client :**

- **Voir le statut :** `sudo systemctl status soundstream` (et `sudo systemctl status mpd` pour le plan de secours local)
- **Arrêter le client :** `sudo systemctl stop soundstream` (et `sudo systemctl stop mpd`)

### Sur macOS

**Pour le Serveur :**

- **Voir le statut :** `brew services list` (Cherchez "mpd" en vert)
- **Arrêter le serveur :** `brew services stop mpd`

**Pour le Client :**

- **Voir le statut (Réseau) :** `launchctl list | grep soundstream`
- **Arrêter le client (Réseau) :** `launchctl stop com.soundstream.receiver`
- **Arrêter le lecteur de secours (Local) :** `mpc stop` (pour stopper la musique) et `brew services stop mpd` (pour stopper le service de secours)