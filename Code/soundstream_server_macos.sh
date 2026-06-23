#!/bin/bash

RED='\033[0;31m'
GREEN='\033[32m'
YELLOW='\033[1;33m'

echo -e "${GREEN}Configuration Serveur SoundStream (Version macOS)${GREEN}"
echo -e "Informations : ANSI escape tout texte ${RED}rouge = erreur${RED} , ${GREEN}vert = informations utile${GREEN}"
echo -e "${YELLOW}Note: Ce script a été adapté pour macOS (Homebrew, LaunchDaemons, macOS Audio).${YELLOW}"

if [ "$EUID" -eq 0 ]; then
	echo -e "${RED}Veuillez NE PAS exécuter ce script avec sudo sur macOS, Homebrew ne le permet pas."
	exit 1
fi

if ! command -v brew &>/dev/null; then
    echo -e "${RED}Homebrew n'est pas installé. Veuillez l'installer d'abord : https://brew.sh/"
    exit 1
fi

echo "Mise à jour du système (via Homebrew)"
brew update && brew upgrade
user=${USER}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [ "$1" == "i" ]; then
	if ! command -v tailscale &>/dev/null; then
 		brew install tailscale
		echo "Veuillez démarrer Tailscale via l'application ou avec 'sudo tailscaled install-system-daemon' puis 'tailscale up'"
	else
		echo 'tailscale est déjà installé'
	fi

	echo -e "${RED}ATTENTION: La couche 2 et VXLAN ne sont pas supportés nativement sur macOS."
	echo "Création pipes ignorée (Risque d'erreur réseau)..."

	if ! command -v mpd &>/dev/null; then
		brew install mpd mpc
	fi
	if ! command -v ffmpeg &>/dev/null; then
		brew install ffmpeg
	fi

	if command -v mpd &>/dev/null; then
		echo 'configuration de mpd' 
		MPD_CONF="$HOME/.mpdconf"
		
		# Création des dossiers si inexistants
		mkdir -p "$PROJECT_ROOT/Code/app/static/audio"
		mkdir -p "$PROJECT_ROOT/Code/app/static/playlists/m3u"
		mkdir -p "$HOME/.mpd"

		echo "# Fichier généré pour macOS
db_file                 \"$HOME/.mpd/database\"
music_directory         \"$PROJECT_ROOT/Code/app/static/audio\"
playlist_directory      \"$PROJECT_ROOT/Code/app/static/playlists/m3u\"

audio_output {
    type \"fifo\"
    name \"FFmpeg Pipe Output\"
    path \"$PROJECT_ROOT/Code/app/static/playlists/mpd.fifo\"
}" > "$MPD_CONF"
		echo "Configurée dans $MPD_CONF"
		
		echo -e "${GREEN}mpd va lire ces playlists sur les repo du projet ne les supprimez surtout pas"
		echo "à quelle heure ouvre le magasin ?"
		read heure
		echo -e "${YELLOW}Note: Sur macOS, 'at' nécessite d'activer 'atrun' via launchctl."
		echo "./soundstream_server_macos.sh x" | at $heure 2>/dev/null || echo -e "${RED}'at' n'est pas disponible."
	else
		echo -e "${RED} problème avec l'installation de mpd"
	fi		       
fi

if [ "$1" == "x" ]; then
	echo 'Lancement...'
	# Si la config n'existe pas on previent
	if [ ! -f "$HOME/.mpdconf" ]; then
		echo -e "${RED}Erreur: Le fichier ~/.mpdconf n'existe pas. Veuillez exécuter ./soundstream_server_macos.sh i d'abord."
		exit 1
	fi

	brew services restart mpd
	sleep 2 # On attend un peu que MPD demarre bien
	
	echo -e "${RED}Création des pipes VXLAN ignorée sur macOS."
	
	if mpc status &>/dev/null; then
		echo "MPD lancé avec succès"
		mpc listall
		mpc clear
		mpc load playlist || true
		mpc repeat on 
		mpc play
	else
		echo -e "${RED}Erreur : mpc ne peut pas se connecter. Essayez de lancer 'mpd --no-daemon --stdout ~/.mpdconf' pour voir l'erreur exacte."
	fi
fi

if [ "$1" == "q" ]; then
	echo -e "${YELLOW}Arrêt du serveur local SoundStream...${YELLOW}"
	mpc stop 2>/dev/null || true
	brew services stop mpd
	echo -e "${GREEN}Serveur local arrêté avec succès.${GREEN}"
fi
