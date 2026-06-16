from flask import render_template, session, redirect, url_for, request
from app import app
from app.services.TimeTableService import TimeTableService
from app.services.LogService import LogService
from app.services.OrganisationService import OrganisationService
from app.services.FileService import FileService
from app.services.SongPlayerService import SongPlayerService
from app.services.UserService import UserService
import datetime

us = UserService()
sps = SongPlayerService()
orga = OrganisationService()
log = LogService()
ts = TimeTableService()
file_service = FileService()

class TimetableController:

    @app.route('/timetable/<nom_orga>', methods=['GET'])
    def timetable(nom_orga):
        metadata = {'title': 'Timetable'}
        context = {
            'metadata': metadata,
            'orga': nom_orga,
            'ts': ts
        }
        return render_template('timetable.html', context=context)

    ####################
    ## EDIT PLAYLISTS ##
    ####################

    @app.route('/createPlaylist/<nom_orga>', methods=['POST'])
    def createPlaylist(nom_orga):
        playlist_name = request.form.get('playlist_name')
        ts.createPlaylist(playlist_name)
        return redirect(url_for('editPlaylist', nom_orga=nom_orga))

    @app.route('/editPlaylist/<nom_orga>', methods=['GET'])
    def editPlaylist(nom_orga):
        metadata = {'title': 'Edit Playlist'}

        playlists = ts.getAllPlaylists()

        selected_playlist_id = request.args.get('playlist_id')
        selected_playlist = None
        files = []
        title_count = 0
        ads_count = 0

        if selected_playlist_id:
            details = ts.getPlaylistDetails(int(selected_playlist_id))
            if details:
                selected_playlist = details['playlist']
                files = details['files']
                title_count = details['title_count']
                ads_count = details['ads_count']

        context = {
            'metadata': metadata,
            'orga': nom_orga,
            'playlists': playlists if playlists else [],
            'selected_playlist': selected_playlist,
            'files': files,
            'title_count': title_count,
            'ads_count': ads_count
        }
        return render_template('edit_playlist.html', context=context)


    @app.route('/choosePlaylist/<nom_orga>', methods=['POST'])
    def choosePlaylist(nom_orga):
        playlist_id = request.form.get('playlist_id')
        return redirect(url_for('editPlaylist', nom_orga=nom_orga, playlist_id=playlist_id))


    @app.route('/addFileToPlaylist/<nom_orga>/<int:playlist_id>', methods=['POST'])
    def addFileToPlaylist(nom_orga, playlist_id):

        if 'uploadfile' not in request.files:
            return redirect(url_for('editPlaylist', nom_orga=nom_orga, playlist_id=playlist_id))

        file_storage = request.files['uploadfile']
        form = request.form

        # Handles physical save (disk) and database entry creation
        file_id = file_service.createFileFromForm(form, file_storage)

        # Proceed only if the file upload was successful
        if file_id != -1:

            # Link file to playlist via TimeTableService
            ts.addFileInPlaylist(playlist_id, file_id)

            ts.updateM3uFile(playlist_id)

            # Log the file addition
            username = session.get('username')
            orga_id = orga.getIdByName(session.get('organisation_name'))
            playlist_name = ts.getPlaylistNameById(playlist_id)

            devices = sps.findAllSongPlayerByOrganisation(orga_id)
            for device in devices:
                if device['state'] == 'ONLINE':
                    # Synchronize files to the device
                    sps.sync_to_device(device['IP_adress'], device['device_name'])

            log.createLog(
                "ADD_FILE",
                f"User {username} added file {file_storage.filename} to playlist {playlist_name}.",
                datetime.datetime.now(),
                orga_id
            )

        return redirect(url_for('editPlaylist', nom_orga=nom_orga, playlist_id=playlist_id))

    @app.route('/deletePlaylist/<nom_orga>', methods=['POST'])
    def deletePlaylist(nom_orga):
        username = session.get('username')
        playlist_id = request.form.get('playlist_id')
        playlist = ts.getPlaylistById(playlist_id)
        user_orga = us.getOrganisationByUsername(username)
        orga_id = orga.getIdByName(user_orga)

        log.createLog(
            "DELETE",
            f"{username} deleted playlist {playlist.name}.",
            datetime.datetime.now(),
            orga_id
        )

        ts.deletePlaylist(playlist_id)

        return redirect(url_for('editPlaylist', nom_orga=nom_orga))

    @app.route('/deleteFileFromPlaylist/<nom_orga>/<int:playlist_id>/<int:file_id>', methods=['GET'])
    def deleteFileFromPlaylist(nom_orga, playlist_id, file_id):

        # Attempt to remove the file via Service
        is_removed = ts.deleteFileFromPlaylist(playlist_id, file_id)

        # Log only if the deletion was successful
        if is_removed:
            username = session.get('username')
            orga_id = orga.getIdByName(session.get('organisation_name'))
            playlist_name = ts.getPlaylistNameById(playlist_id)

            ts.updateM3uFile(playlist_id)

            log.createLog(
                "REMOVE_FILE",
                f"User {username} removed file {file_id} from playlist {playlist_name}.",
                datetime.datetime.now(),
                orga_id
            )

        return redirect(url_for('editPlaylist', nom_orga=nom_orga, playlist_id=playlist_id))


    ############################
    ## EDIT PLAYLIST FOR DAYS ##
    ############################

    @app.route('/editTables/<nom_orga>', methods=['GET'])
    def editTables(nom_orga):
        metadata = {'title': 'Edit Tables'}
        days_with_playlists = ts.getAllDaysWithPlaylists()
        all_playlists = ts.getAllPlaylists()

        context = {
            'metadata': metadata,
            'orga': nom_orga,
            'days_with_playlists': days_with_playlists,
            'all_playlists': all_playlists if all_playlists else []
        }
        return render_template('edit_tables.html', context=context)

    @app.route('/updateDay/<nom_orga>', methods=['POST'])
    def updateDay(nom_orga):
        day_name = request.form.get('day_name')
        playlist_id = request.form.get('playlist_id')
        start_time = request.form.get('start_time')
        if playlist_id:
            playlist_id = int(playlist_id)
        else:
            playlist_id = None
        ts.updateDaySchedule(day_name, playlist_id, start_time)

        # Log the schedule update
        playlist = ts.getPlaylistById(playlist_id)
        username = session.get('username')
        orga_id = orga.getIdByName(session.get('organisation_name'))
        log.createLog("SCHEDULE_UPDATE",
                            f"User {username} updated the schedule for playlist {playlist.name}.",
                           datetime.datetime.now(),
                             orga_id)

        return redirect(url_for('editTables', nom_orga=nom_orga))