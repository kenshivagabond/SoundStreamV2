#!/bin/bash

RED='\033[0;31m'
GREEN='\033[32m'
YELLOW='\033[1;33m'

echo -e "${GREEN}Configuration Client SoundStream (Version macOS)${GREEN}"
echo -e "Informations : ANSI escape tout texte ${RED}rouge = erreur${RED} , ${GREEN}vert = informations utile${GREEN}"
echo -e "${YELLOW}Note: Ce script a été adapté pour macOS (Homebrew, LaunchDaemons, macOS Audio).${YELLOW}"

if [ "$EUID" -eq 0 ]; then
	echo -e "${RED}Veuillez NE PAS exécuter ce script avec sudo sur macOS, Homebrew ne le permet pas."
	exit 1
fi

if ! command -v brew &>/dev/null; then
    echo -e "${RED}Homebrew n'est pas installé."
    exit 1
fi

echo "Mise à jour via Homebrew"
brew update
user=${USER}

if [ "$1" == "i" ]; then
	if ! command -v tailscale &>/dev/null; then
 		brew install tailscale
		echo "Veuillez démarrer Tailscale via l'application ou avec 'sudo tailscaled install-system-daemon' puis 'tailscale up'"
	else
		echo 'tailscale est déjà installé'
	fi

	echo -e "${RED}ATTENTION: La couche 2 et VXLAN ne sont pas supportés nativement sur macOS."
	echo "Création pipes ignorée..."

	if ! command -v mpd &>/dev/null; then
		brew install mpd mpc
	fi
	if ! command -v ffmpeg &>/dev/null; then
		brew install ffmpeg # Inclut ffplay
	fi

	if command -v mpd &>/dev/null; then
		echo 'configuration de mpd (cas où le réseau tombe)' 
		MPD_CONF="$HOME/.mpdconf"
		
		mkdir -p "$HOME/.mpd"
		mkdir -p "$HOME/audio"
		mkdir -p "$HOME/playlists"

		echo "# Config macOS
db_file                 \"$HOME/.mpd/database\"
music_directory         \"$HOME/audio\"
playlist_directory      \"$HOME/playlists\"

audio_output {
    type \"osx\"
    name \"Mac CoreAudio Output\"
}" > "$MPD_CONF"
		echo "Configurée dans $MPD_CONF"
		
		echo "Création d'un LaunchAgent pour ffplay"
		PLIST_PATH="$HOME/Library/LaunchAgents/com.soundstream.receiver.plist"
		mkdir -p "$HOME/Library/LaunchAgents"
		
		echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>Label</key>
    <string>com.soundstream.receiver</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which ffplay)</string>
        <string>-nodisp</string>
        <string>-flags</string>
        <string>low_delay</string>
        <string>rtp://239.1.1.1:5004</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>" > "$PLIST_PATH"

		launchctl unload "$PLIST_PATH" 2>/dev/null || true
		launchctl load -w "$PLIST_PATH"
		echo "Service LaunchAgent chargé."
		
		echo "à quelle heure ouvre le magasin ?"
		read heure
		echo -e "${YELLOW}Note: Sur macOS, 'at' nécessite d'activer 'atrun' via launchctl."
		echo "./soundstream_client_macos.sh x" | at $heure 2>/dev/null || echo -e "${RED}'at' n'est pas disponible."
	else
		echo -e "${RED} problème avec l'installation de mpd"
	fi		       
fi

if [ "$1" == "x" ]; then
	echo 'Lancement...'
	if [ ! -f "$HOME/.mpdconf" ]; then
		echo -e "${RED}Erreur: Le fichier ~/.mpdconf n'existe pas. Veuillez exécuter ./soundstream_client_macos.sh i d'abord."
		exit 1
	fi

	echo -e "${RED}Configuration VXLAN ignorée sur macOS."
	
	if ping -c 4 224.0.0.0 &> /dev/null; then
		echo "Lien réseau multicast (simulé) OK "
		echo "Lancement du stream via LaunchAgent" 
		launchctl start com.soundstream.receiver
	else
		brew services restart mpd 
		sleep 2
		echo -e "${RED}Lien réseau : erreur : plan d'urgence (local)"
		if mpc status &>/dev/null; then
			mpc clear
			FIRST_PLAYLIST=$(mpc lsplaylists | head -n 1)
			if [ -n "$FIRST_PLAYLIST" ]; then
				echo -e "${GREEN}Chargement de la playlist locale : $FIRST_PLAYLIST"
				mpc load "$FIRST_PLAYLIST"
				mpc repeat on 
				mpc play
			else
				echo -e "${GREEN}Aucune playlist locale trouvée. En attente du serveur..."
			fi
		else
			echo -e "${RED}Erreur : mpc ne peut pas se connecter à mpd."
		fi
	fi
fi

if [ "$1" == "status" ]; then
	echo -e "${GREEN}=== Musiques en attente (Playlist) ===${GREEN}"
	mpc playlist
	echo -e "\n${GREEN}=== État du lecteur ===${GREEN}"
	mpc status
fi

if [ "$1" == "monitor" ]; then
	echo -e "${GREEN}Lancement du monitoring en direct... (Ctrl+C pour quitter)${GREEN}"
	echo -e "${YELLOW}[PLAYLIST INITIALE]${YELLOW}"
	mpc playlist | sed 's/^/  - /'
	echo -e "${GREEN}[LECTURE INITIALE] $(mpc current)${GREEN}"
	
	# idleloop écoute en direct les changements d'état du lecteur et de la playlist
	mpc idleloop player playlist | while read event; do
		if [ "$event" = "player" ]; then
			current=$(mpc current)
			if [ -n "$current" ]; then
				echo -e "${GREEN}[LIVE] 🎵 Nouvelle lecture en cours : $current${GREEN}"
			else
				echo -e "${RED}[LIVE] ⏹ Lecture arrêtée.${RED}"
			fi
		elif [ "$event" = "playlist" ]; then
			echo -e "${YELLOW}[PLAYLIST] 📝 La liste de lecture a été modifiée :${YELLOW}"
			mpc playlist | sed 's/^/  - /'
		fi
	done
fi

if [ "$1" == "q" ]; then
	echo -e "${YELLOW}Arrêt du client SoundStream...${YELLOW}"
	mpc stop 2>/dev/null || true
	brew services stop mpd
	launchctl stop com.soundstream.receiver 2>/dev/null || true
	echo -e "${GREEN}Client arrêté avec succès.${GREEN}"
fi
