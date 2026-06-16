import threading
import subprocess
import time
import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from app import app
from app.models.SongPlayerDAO import SongPlayerDAO
from app.services.TimeTableService import TimeTableService
import ping3

ts = TimeTableService()

class SongPlayerService:

    _current_playlist = None

    def __init__(self):
        self.spdao = SongPlayerDAO()


    def deleteSongPlayer(self, id_song_player):
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
        return self.findAll()


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
            self.spdao.UpdateState(player.IP_adress)

        # Retrieve the updated objects from the database after synchronization
        updated_players = self.spdao.findAllByOrganisationInBd(id_orga)

        # Convert objects to dictionaries for compatibility with Jinja2 templates
        player_list_dict = []
        for player in updated_players:
            player_list_dict.append(vars(player))

        return player_list_dict


    def countNumberOfSongPlayerOnlineAndOffline(self, id_orga):
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


    def run_sync(self, player: dict) -> dict:
        """Synchronize audio and playlist files to a remote device via rsync."""
        try:
            device_name = player.get('name')
            ip = player.get('ip')
            sync_tasks = [
                (os.path.join(app.static_folder, 'audio/'), "music/"),
                (os.path.join(app.static_folder, 'playlists/'), "playlists/")
            ]
            base_dest_path = f"/home/{device_name}"
            for src, subfolder in sync_tasks:
                full_remote_path = f"{base_dest_path}/{subfolder}"
                dest = f"{device_name}@{ip}:{full_remote_path}"
                cmd = ["rsync", "-avz", "--delete", "-e", "ssh", src, dest]
                try:
                    subprocess.run(cmd, check=True)
                    print(f"[{device_name}]: Files sent successfully")
                except Exception as e:
                    print(f"[{device_name}]: Sync failed")
        except Exception as e:
            print(f"Error in run_sync: {e}")

        return player


    def multi_thread_rsync(self):
        """Multi-threaded file synchronization using rsync."""
        devices = self.spdao.findDevices()

        with ThreadPoolExecutor(max_workers=min(len(devices), 10)) as executor:
            list(executor.map(self.run_sync, devices))


    def run_check(self):
        """Background scheduler loop: checks the current schedule and switches playlists accordingly."""
        print("Scheduler started...")
        while True:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_day = now.strftime("%A")
            scheduled_playlist = ts.getPlaylistForTime(current_day, current_time)

            if scheduled_playlist and scheduled_playlist != SongPlayerService._current_playlist:

                devices = self.spdao.findAllOnlineDevices()
                if devices:

                    print(f"Playlist change: {scheduled_playlist}")
                    for dev in devices:
                        self.remote_play_playlist(dev.IP_adress, dev.device_name, scheduled_playlist)

                    # Update the class variable to avoid restarting the same playlist
                    SongPlayerService._current_playlist = scheduled_playlist

            # If no playlist is scheduled at this time (gap in the schedule)
            elif not scheduled_playlist and SongPlayerService._current_playlist is not None:
                print("No playlist is currently scheduled.")
                SongPlayerService._current_playlist = None

            time.sleep(30)

    def start_background_scheduler(self):
        threading.Thread(target=self.run_check, daemon=True).start()

    def findByID(self, id_player: int):
        """ Wrapper to get a device by its ID. """
        return self.spdao.findByID(id_player)

    def updateDbSongPlayer(self, form_data: dict, id_player: int) -> None:
        """ Wrapper to update a device in the database. """
        self.spdao.updateDbSongPlayer(form_data, id_player)

    def findAllBuildingNames(self) -> list:
        """ Wrapper to retrieve all building names. """
        return self.spdao.findAllBuildingNames()

    def createDevice(self, name_place: str, ip_address: str, state: str, place_address: str, place_postcode: str, place_city: str, place_building_name: str, device_name: str, id_orga: int) -> None:
        """ Wrapper to create a new device in the database. """
        self.spdao.createDevice(name_place, ip_address, state, place_address, place_postcode, place_city, place_building_name, device_name, id_orga)

