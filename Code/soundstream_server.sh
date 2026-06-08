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
pacman -Syu

if [ $1 -eq "i" ]then
	if command -v tailscale &>/dev/null; then
		echo 'tailscale est deja installer'
		echo -e "${GREEN}couche 2 non disponible sur tailscale or on veut faire du multicast"
		echo "Creation pipes"
		ip link add dev vx_sound type vxlan id 42 remote 100.94.208.67 local 100.112.176.54 dev tailscale0 dstport 4789
		ip addr add 192.168.100.1/24 dev vx_sound
		ip link set dev vx_sound up
		ip route add 224.0.0.0/4 dev vx_sound
		check=$(ip a | grep "224.0.0.0/4")
		if [ -n "$check" ]; then
			echo "OK"
			if command -v mpd &>/dev/null, then
				echo 'mpd est déjà installer'
		else
			echo -e "${RED}Pb avec Pipe : executer journalctl -xe des erreurs ?"
			exit 1
		fi


	else
 		curl -fsSL https://tailscale.com/install.sh | sh
		tailscale up
		up=$(tailscale status | grep "$(whoami)")

	if [ -n "$up" ]; then
		echo 'installation effectuer avec succés vous pouvez redemarrer le script'
	else
		echo -e "${RED}Une erreur est intervenue lors de l'installation de tailscale : executer journalctl -xe des erreurs ?"
		exit 1
	fi
		
fi
if [ $1 -eq "x" ]then



