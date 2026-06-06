import sqlite3
from app import app
import requests
import subprocess
from ping3 import ping, verbose_ping
import json
from app.models.SongPlayer import SongPlayer
from app.models.SongPlayerDAOInterface import SongPlayerDAOInterface

class SongPlayerDAO(SongPlayerDAOInterface) :

    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'

    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def findDevices(self) -> None:
        """ Reach any devices through tailscale. """
        conn = self._getDbConnection()
        try:
            players = {}
            cmd = subprocess.run(["tailscale","status","--json"],capture_output=True,text=True)
            data = json.loads(cmd.stdout)
            for peer in data['Peer'].values():
                name = peer['HostName'].split('-')[0]
                ip = peer['TailscaleIPs'][0]

                if name not in players:
                    players[name] = {
                                     "name": name,
                                     "ip": ip,
                                     "ville": None,
                                     "orga": None}
            for player in players.values():
                if player['ville'] is None:
                    res = requests.get(f"https://ipinfo.io/{player['ip']}")
                    loc_data = res.json()
                    player["city"] = loc_data["city"]
                    player["orga"] = 1

                query_player = """
                INSERT OR IGNORE  INTO song_player
                (name_place, IP_adress, state, last_synchronization, id_orga)
                VALUES (?,?,"OK",CURRENT_TIMESTAMP,?);"""

                query_loc = """INSERT OR IGNORE INTO localisation (city) VALUES (?);"""

                conn.execute(query_player, (player['name'],player['ip'],player['orga'],player['ville']))
                conn.execute(query_loc,player["ville"])
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
        return  []

    def findByOrganisation(self, name_orga) -> SongPlayer:
        """ Get song player by organisation name """
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player JOIN organisation USING(id_orga) WHERE name_orga = ?;', (name_orga,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers :
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []

    def findByState(self, state) -> SongPlayer:
        """ Get song player by state """
        conn = self._getDbConnection()
        songplayers = conn.execute('SELECT * FROM song_player WHERE state = ;', (state,)).fetchall()
        songplayerList = list()
        for songplayer in songplayers :
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList:
            return songplayerList
        return []

    

    def findAllByOrganisationAndStatus(self, id_orga, status) -> list:
        """ find all song players by organisation and status """
        conn = self._getDbConnection()

        sql = "SELECT * FROM song_player WHERE id_orga = ? AND state = ?;"

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
        for songplayer in songplayers :
            songplayerList.append(SongPlayer(dict(songplayer)))
        conn.close()

        if songplayerList :
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

    def UpdateState(self, ip) -> None :
        """ Really updates player states (via ping) """
        conn = self._getDbConnection()
        if ping(ip) != None:
            conn.execute('UPDATE song_player SET state = ONLINE WHERE ip =  ?;', (ip))
        conn.commit()
        conn.close()

    def findAllOnlineDevices(self) -> list[SongPlayer]:
        conn = self._getDbConnection()
        songplayers = conn.execute("SELECT * FROM song_player WHERE state = 'ONLINE';").fetchall()
        players_online_list = list()

        for songplayer in songplayers :
            players_online_list.append(SongPlayer(dict(songplayer)))

        conn.close()
        return players_online_list
 
