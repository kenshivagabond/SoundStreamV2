from app.models.SongPlayerDAO import SongPlayerDAO
from app.services.TimeTableService import TimeTableService 
import subprocess
import time
import threading
import datetime
import platform
import os
from app import app
import ping3

ts = TimeTableService()

class SongPlayerService:

    _current_playlist = None
    
    def __init__(self) :
        self.spdao = SongPlayerDAO()
  
        

   
    def deleteSongPlayer(self,id_song_player):
        """
        Deletes a song player from the system and the database.

            Args:
                id_song_player (int): The unique identifier of the player to be removed.
        """

        self.spdao.deleteSongPlayerInDb(id_song_player)


    def allSongPlayer(self):
        """
        Retrieves all song players available in the system.

            Returns:
                List[SongPlayer]: A list containing all song player instances.
        """
        return  self.findAll()
 
                                            
    def findAllSongPlayerByOrganisation(self, id_orga):
        """
        Retrieves and synchronizes the status of all players within an organization.

            Args:
                id_orga (int): The unique ID of the organization.

            Returns:
                list[dict]: A list of song players as dictionaries with refreshed network statuses.
        """
        # Fetch initial list of players to identify who needs to be checked
        self.spdao.findDevices()
        players = self.spdao.findAllByOrganisationInBd(id_orga)

        # Update each player's status by pinging their IP address
        for player in players:
            spdao.UpdateState(player.ip);

        # Retrieve the updated objects from the database after synchronization
        updated_players = self.spdao.findAllByOrganisationInBd(id_orga)

        # Convert objects to dictionaries for compatibility with Jinja2 templates
        player_list_dict = []
        for player in updated_players:
            player_list_dict.append(vars(player))
    
        return player_list_dict
    
    
    #def addSongPlayer(self,form):


    def countNumberOfSongPlayerOnlineAndOffline(self,id_orga) :
        """
        Counts the number of online and offline song players for a specific organization.

            Args:
                id_orga (int): The unique ID of the organization.

            Returns:
                tuple: A tuple containing (nb_on, nb_off).
        """
        # Initialize counters for online and offline states
        nb_on = 0
        nb_off = 0

        # Retrieve the list of players as dictionaries from the service
        liste_song_player = self.spdao.findAllByOrganisationInBd(id_orga)

        # Convert objects to dictionaries for compatibility with Jinja2 templates
        liste_song_player_dict = [vars(p) for p in liste_song_player]
        
        # Iterate through the list to count states
        for p in liste_song_player_dict:
            if p['state'] == 'ONLINE':
                nb_on += 1
            elif p['state'] == 'OFFLINE':
                nb_off += 1

        return (nb_on, nb_off)
        

    def run_sync(self, ip, device_name):
            # Configuration des dossiers
            # On définit des couples (Source_Locale, Dossier_Destination_Distant)
            sync_tasks = [
                (os.path.join(app.static_folder, 'audio/'), "music/"),
                (os.path.join(app.static_folder, 'playlists/'), "playlists/")
            ]
            
            base_dest_path = f"/home/{device_name}/SoundStreamDevice/"
            for src, subfolder in sync_tasks:
                full_remote_path = os.path.join(base_dest_path, subfolder)
                
                subprocess.run(["ssh", f"{device_name}@{ip}", f"mkdir -p {full_remote_path}"])

                dest = f"{device_name}@{ip}:{full_remote_path}"
                cmd = [
                    "rsync", "-avz", "--delete",
                    "-e", "ssh",
                    src, dest
                ]
                
                try:
                    subprocess.run(cmd, check=True)
                except Exception as e:
                    print(f"Erreur synchro {subfolder} vers {ip} : {e}")
                    
            threading.Thread(target=self.run_sync, args=(ip, device_name)).start()
    
    def run_check(self):
        print("Scheduler démarré...")
        while True:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_day = now.strftime("%A")
            scheduled_playlist = ts.getPlaylistForTime(current_day, current_time)
            
            if scheduled_playlist and scheduled_playlist != SongPlayerService._current_playlist:
                
                devices = self.spdao.findAllOnlineDevices()
                if devices:

                    print(f"Changement de playlist : {scheduled_playlist}")
                    for dev in devices:
                        self.remote_play_playlist(dev.IP_adress, dev.device_name, scheduled_playlist)
                    
                    # On met à jour la variable de classe pour ne pas relancer la même playlist
                    SongPlayerService._current_playlist = scheduled_playlist
            
            # Si aucune playlist n'est prévue dans le planning (trou dans l'emploi du temps)
            elif not scheduled_playlist and SongPlayerService._current_playlist is not None:
                print("Aucune playlist n'est programmée actuellement.")
                SongPlayerService._current_playlist = None

            time.sleep(30)

    def start_background_scheduler(self):

        threading.Thread(target=self.run_check, daemon=True).start()


