#!/bin/bash

RED='\033[0;31m' # test des ANSI escape parcque pq pas
GREEN='\033[32m'


echo 'Configuration Serveur SoundStream '
ascii-image-converter -C 1.png
echo 'informations : ANSI escape tout text rouge = erreur , vert = informations utile'
echo -e "${GREEN} SoundStreamV2 est une mise à jour d'un autre projet universitaires , encore merci d'implantées nos solutions 
comme dit sur le readme i permet d'initier l'installation , x permet d'executer le programme avec at , on utilise x car i fait beaucoup de chose"
if [ "$EUID" -ne 0 ]; then
	echo -e "${RED}Vous n'êtes pas en super user , executer ce scripte avec sudo"
	exit 1
fi
echo "Application de mise à jour (il faudra souvent aprés cela rédemarrer sur Arch)"
pacman -Syu --noconfirm
user=${SUDO_USER:-$(whoami)} # On est en super utilisateur , moyen pour récupérer l'utilisateur actuelle dans tout les cas

if [ "$1" == "i" ];then
	if command -v tailscale &>/dev/null; then
		echo 'tailscale est deja installer'
		echo -e "${GREEN}couche 2 non disponible sur tailscale or on veut faire du multicast"
		echo "Creation pipes"
		ip link add dev vx_sound type vxlan id 42 remote 100.94.208.67 local 100.112.176.54 dev tailscale0 dstport 4789
		ip addr add 192.168.100.1/24 dev vx_sound
		ip link set dev vx_sound up
		ip route add 224.0.0.0/4 dev vx_sound
		check=$(ip route | grep "224.0.0.0/4")
		if [ -n "$check" ]; then
			echo "OK"
			if command -v mpd &>/dev/null; then
				echo 'mpd est déjà installer'
				echo 'configuration de mpd' 
				rm /etc/mpd.conf
				echo "# See: /usr/share/doc/mpd/mpdconf.example

					db_file                 "/var/lib/mpd/tag_cache"

					music_directory  "/home/$user/Documents/SoundStreamV2/Code/app/static/audio"

					playlist_directory "/home/$user/Documents/SoundStreamV2/Code/app/static/playlists/m3u"

					audio_output {
        					type "fifo"
        					name "FFmpeg Pipe Output"
						path "/home/$user/Documents/SoundStreamV2/Code/app/static/playlists/mpd.fifo"

					}	
				" > /etc/mpd.conf
				echo "configurée"
				if command -v ffmpeg &>/dev/null; then
					echo 'ffmpeg est déjà installer'
					echo -e "${GREEN}mpd va lire ces playlists sur les repo du projet ne les supprimer surtout pas ou modifier le fichier de conf"
					echo "à quelle heure ouvre le magasin ?"
					read heure
					echo "./soundstream_server.sh x" | at $heure
				else
					pacman -S --noconfirm ffmpeg
					if command -v ffmpeg &>/dev/null; then
						echo 'installation de ffmpeg effectuer avec succées vous pouvez redemarrer le script'
					else 
						echo -e "${RED} pb avec l'installation de ffmpeg : executer journalctl -xe des erreurs ?"
					fi
				fi
			else
			       pacman -S --noconfirm mpd mpc
		       	       if command -v mpd &>/dev/null; then
			  		echo 'installation de mpd avec succés vous pouvez redemarrer le script'
			 	else
					echo -e "${RED} pb avec l'installation de mpd : executer journalctl -xe des erreurs ?"
			       fi
	       		fi		       

		else
			echo -e "${RED}Pb avec Pipe : executer journalctl -xe des erreurs ?"
			exit 1
		fi


	else
 		pacman -S --noconfirm tailscale
		tailscale up
		up=$(tailscale status | grep "$user")

		if [ -n "$up" ]; then
			echo 'installation effectuer avec succés vous pouvez redemarrer le script'
		else
			echo -e "${RED}Une erreur est intervenue lors de l'installation de tailscale : executer journalctl -xe des erreurs ?"
			exit 1
		fi
	fi
		
fi
if [ "$1" == "x" ];then
fi


