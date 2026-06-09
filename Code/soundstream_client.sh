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
echo "Application de mise à jour "
pacman -Syu --noconfirm
user=${SUDO_USER:-$(whoami)} # On est en super utilisateur , moyen pour récupérer l'utilisateur actuelle dans tout les cas

if [ "$1" == "i" ];then
	if command -v tailscale &>/dev/null; then
		echo 'tailscale est deja installer'
		echo -e "${GREEN}couche 2 non disponible sur tailscale or on veut faire du multicast"
		echo "Creation pipes"
		ip link add dev vx_sound type vxlan id 42 remote 100.112.176.54 local 100.94.208.67 dev tailscale0 dstport 4789
		ip addr add 192.168.100.1/24 dev vx_sound
		ip link set dev vx_sound up
		ip route add 224.0.0.0/4 dev vx_sound
		check=$(ip route | grep "224.0.0.0/4")
		if [ -n "$check" ]; then
			echo "OK"
			if command -v mpd &>/dev/null; then
				echo 'mpd est déjà installer'
				echo 'configuration de mpd (cas ou le reseau tombe)' 
				rm /etc/mpd.conf
				echo "# See: /usr/share/doc/mpd/mpdconf.example

					db_file                 "/var/lib/mpd/tag_cache"

					music_directory  "/home/$user/audio"

					playlist_directory "/home/$user/playlists"

					audio_output {
        					type "alsa"
        					name "FFmpeg ALSA Output"

					}	
				" > /etc/mpd.conf
				echo "configurée"
				if command -v ffplay &>/dev/null; then
					echo 'ffplay est déjà installer'
					echo "Creation d'un service ffplay"
					touch /etc/systemd/system/soundstream.service
					echo "[Unit]
					      Description=SOUNDSTREAM RTP RECEIVER 
					      After=network-online.target
					      Wants=network-online.target

					     [Service]
				             Type=simple
					     User=$user
					     Environment=ALSA_CARD=1
				             ExecStart=/usr/bin/ffplay -flags low_delay rtp://239.1.1.1:5004
					     Restart=always
					     RestartSec=5

					     [Install]
					     WantedBy=multi-user.target
					     " > /etc/systemd/system/soundstream.service
					     systemctl reload-demon
					     systemctl start soundstream
					     another_check=$(systemctl status soundstream | "enable")
					     if [ -n "$another_check" ]; then
						     echo "OK"
						     echo "à quelle heure ouvre le magasin ?"
                                        	     read heure
                                        	     echo "./soundstream_client.sh x" | at $heure


					     else
						     echo -e "${RED} Pb niveau service : executer journalctl -xeu soundstream.service des erreurs ?"

				else
					sudo apt install --noconfirm ffplay
					if command -v ffplay &>/dev/null; then
						echo 'installation de ffmpeg effectuer avec succées vous pouvez redemarrer le script'
					else 
						echo -e "${RED} pb avec l'installation de ffmpeg : executer journalctl -xe des erreurs ?"
					fi
				fi
			else
			       sudo apt install --noconfirm mpd mpc
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
 		sudo apt install --noconfirm tailscale
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
	echo 'Lancement...'
	echo "${GREEN} Malheuresement on doit s'occuper de la couche 2 à chaque démarrage"
	echo "Creation pipes"
        ip link add dev vx_sound type vxlan id 42 remote 100.112.176.54 local 100.94.208.67  dev tailscale0 dstport 4789
        ip addr add 192.168.100.1/24 dev vx_sound
        ip link set dev vx_sound up
        ip route add 224.0.0.0/4 dev vx_sound
        check=$(ip route | grep "224.0.0.0/4")
        if [ -n "$check" ]; then
                        echo "pipe : OK"
			if ping -c 4 224.0.0.0 &> /dev/null; then
				echo "Lien avec le Pipe OK "
				echo "Lancement du stream" 
				systemctl start soundstream
			else
				systemctl start mpd 
				echo "${RED}Lien avec le Pipe : erreur : plan d'urgence"
				mpc listall
				mpc clear
				mpc load playlist
				mpc repeat on 
				mpc play
			else
				echo -e "${RED}Pb avec MPD : executer journalctl -xeu mpd.service : des erreurs ?"
	else 
		echo -e "${RED} Pb avec pipe, : executer journalctl -xe des erreurs ?"

	fi
fi



