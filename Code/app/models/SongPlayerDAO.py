import sqlite3
import subprocess
import json
import paramiko
from concurrent.futures import ThreadPoolExecutor
from ping3 import ping
from app import app
from app.models.SongPlayer import SongPlayer
from app.models.SongPlayerDAOInterface import SongPlayerDAOInterface

class SongPlayerDAO(SongPlayerDAOInterface):

    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'

    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn


    def sshForMultiThread(self, player: dict) -> dict:
        """SSH into a device to retrieve its public IP and geolocation (used by findDevices in multi-threaded mode)."""
        player["has_client"] = False
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
            player["ip"], 
            timeout=5)
            
            # Check for SoundStream client presence (mpc)
            # Add common paths (like homebrew) to PATH since non-interactive SSH might not have them
            stdin, stdout, stderr = ssh.exec_command("PATH=$PATH:/opt/homebrew/bin:/usr/local/bin command -v mpc")
            if stdout.channel.recv_exit_status() == 0:
                player["has_client"] = True

            stdin, stdout, stderr = ssh.exec_command("curl -s https://api.ipify.org")
            public_ip = stdout.read().decode('utf-8').strip()

            import requests
            res = requests.get(f"https://ipinfo.io/{public_ip}")
            loc_data = res.json()
            player["ville"] = loc_data["city"]
            player["orga"] = 1
            ssh.close()

            return player
        except Exception as e:
            print(f"SSH connection failed for {player['ip']}")

        return player


    def findDevices(self) -> None:
        """ Reach any devices through tailscale. """
        conn = self._getDbConnection()

        try:
            players = {}
            cmd = subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True)
            data = json.loads(cmd.stdout)
            
            # Add the current machine (Self) to the devices list
            if 'Self' in data:
                self_node = data['Self']
                name_self = self_node['DNSName'].split('.')[0].split('-')[0] if self_node['HostName'].lower() == 'localhost' else self_node['HostName'].split('-')[0]
                ip_self = self_node['TailscaleIPs'][0]
                players[name_self] = {"name": name_self, "ip": ip_self, "ville": None, "orga": 1}

            for peer in data.get('Peer', {}).values():
                # Fix for iOS devices returning 'localhost' as HostName
                if peer['HostName'].lower() == 'localhost' and 'DNSName' in peer:
                    name = peer['DNSName'].split('.')[0]
                else:
                    name = peer['HostName'].split('-')[0]
                ip = peer['TailscaleIPs'][0]

                if name not in players:
                    players[name] = {
                                     "name": name,
                                     "ip": ip,
                                     "ville": None,
                                     "orga": 1,
                                     "has_client": False}

            with ThreadPoolExecutor(max_workers=len(players)) as executor:
                updated_players = list(executor.map(self.sshForMultiThread, players.values()))

                query_player = """
                INSERT INTO song_player
                (name_place, IP_adress, state, has_client, last_synchronization, id_orga, place_adress, place_postcode, place_city, device_name)
                VALUES (?, ?, "OK", ?, CURRENT_TIMESTAMP, ?, 'Inconnue', '00000', ?, ?)
                ON CONFLICT(IP_adress) DO UPDATE SET
                    has_client = excluded.has_client,
                    last_synchronization = excluded.last_synchronization;"""

                for player in updated_players:
                    ville = player["ville"] if player["ville"] else "Inconnue"
                    has_client_val = 1 if player.get("has_client") else 0
                    conn.execute(
                        query_player,
                        (
                            player["name"],
                            player["ip"],
                            has_client_val,
                            player["orga"],
                            ville,
                            player["name"]
                        )
                    )

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()



    def findByID(self, id_player) -> SongPlayer:
        """ Get song player by the id of the song player """
        conn = self._getDbConnection()
        # Use a parameterized query to prevent SQL injection
        res = conn.execute('SELECT * FROM song_player WHERE id_player = ?;', (id_player,)).fetchone()
        conn.close()

        if res:
            return SongPlayer(dict(res))
        return []

    def findByOrganisation(self, name_orga) -> SongPlayer:
        """ Get song player by organisation name """
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player JOIN organisation USING(id_orga) WHERE name_orga = ?;', (name_orga,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers:
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []

    def findAllByOrganisationInBd(self, id_orga) -> list:
        """ Get all song players by organisation ID """
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player WHERE id_orga = ? AND has_client = 1;', (id_orga,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers:
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        return songplayerList

    def findByState(self, state) -> SongPlayer:
        """ Get song player by state """
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player WHERE state = ?;', (state,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers:
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []



    def findAllByOrganisationAndStatus(self, id_orga, status) -> list:
        """ Find all song players by organisation and status """
        conn = self._getDbConnection()

        sql = "SELECT * FROM song_player WHERE id_orga = ? AND state = ? AND has_client = 1;"

        songplayers = conn.execute(sql, (id_orga, status)).fetchall()

        songplayerList = list()
        for songplayer in songplayers:
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []

    def findAll(self) -> list[SongPlayer]:
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player;').fetchall()
        songplayerList = list()
        for songplayer in songplayers:
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []

    def findAllBuildingNames(self) -> list:
        """Get all distinct building names from the song players."""
        conn = self._getDbConnection()
        query = "SELECT DISTINCT place_building_name FROM song_player;"
        cursor = conn.execute(query)
        results_query = cursor.fetchall()
        conn.close()

        # Extract building names from the result set
        building_names = []
        for row_query in results_query:
            building_names.append(row_query['place_building_name'])

        return building_names

    def UpdateState(self, ip) -> None:
        """ Update player state based on whether mpc is responding """
        conn = self._getDbConnection()
        try:
            import subprocess
            cmd = [
                "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=1", ip,
                "PATH=$PATH:/opt/homebrew/bin:/usr/local/bin mpc status"
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=2)
            if result.returncode == 0:
                conn.execute("UPDATE song_player SET state = 'ONLINE' WHERE IP_adress = ?;", (ip,))
            else:
                conn.execute("UPDATE song_player SET state = 'OFFLINE' WHERE IP_adress = ?;", (ip,))
        except Exception:
            conn.execute("UPDATE song_player SET state = 'OFFLINE' WHERE IP_adress = ?;", (ip,))
            
        conn.commit()
        conn.close()

    def findAllOnlineDevices(self) -> list[SongPlayer]:
        conn = self._getDbConnection()
        songplayers = conn.execute("SELECT * FROM song_player WHERE state = 'ONLINE' AND has_client = 1;").fetchall()
        players_online_list = list()

        for songplayer in songplayers:
            players_online_list.append(SongPlayer(dict(songplayer)))

        conn.close()
        return players_online_list
