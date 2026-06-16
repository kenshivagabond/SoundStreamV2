from flask import render_template, session, redirect, url_for, request, jsonify
import datetime
from app import app
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.SongPlayerService import SongPlayerService
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService


log = LogService()
sps = SongPlayerService()
ogs = OrganisationService()

class DevicesController:

    @app.route('/devices/<nom_orga>', methods=['GET'])
    @LoggedIn
    def devices(nom_orga):

        metadata = {'title': 'Devices'}
        # Get organization ID once to optimize database queries
        id_orga = ogs.getIdByName(nom_orga)

        # Get all players for this organization as a list of dictionaries
        liste_song_player_dict = sps.findAllSongPlayerByOrganisation(id_orga)

        # Retrieve the count of online and offline players for this organization
        nb_on_and_nb_off = sps.countNumberOfSongPlayerOnlineAndOffline(id_orga)

        # Unpack counters from the result tuple
        nb_on = nb_on_and_nb_off[0]
        nb_off = nb_on_and_nb_off[1]

        context = {
            'metadata': metadata,
            'orga': nom_orga,
            'liste_song_player': liste_song_player_dict,
            'nb_on': nb_on,
            'nb_off': nb_off
        }
        return render_template('devices.html', context=context)


    @app.route('/update/<int:id_player>', methods=['POST', 'GET'])
    @LoggedIn
    def update(id_player):

        # Run the ping test and save the new status (PLAYING/OFFLINE) in the database
        sps.changeState(id_player)

        # Redirect the user back to the previous page to see the updated status
        return redirect(request.referrer)


    @app.route('/delete/<int:id_player>', methods=['POST', 'GET'])
    @LoggedIn
    @reqrole(['admin'])
    def delete(id_player):

        player = sps.findByID(id_player)
        log.createLog(
            "DELETE",
            f"Player {player.name_place} has been deleted",
            datetime.datetime.now(),
            player.id_orga)
        # Permanently remove the player from the database using the service layer
        sps.deleteSongPlayer(id_player)

        # Stay on the current page to confirm the player is gone from the list
        return redirect(request.referrer)


    # This route only transits JSON data (no HTML rendering).
    # It is used for auto-refresh of device statuses via AJAX requests.
    @app.route('/auto_update_status/<nom_orga>')
    @LoggedIn
    def get_status(nom_orga):

        # Get the organization ID
        id_orga = ogs.getIdByName(nom_orga)

        # Retrieve the list of players for this organization
        players = sps.findAllSongPlayerByOrganisation(id_orga)
        status_data = []

        for p in players:
            # Trigger a ping for each player to update the database
            sps.changeState(p['id_player'])

            # Prepare minimal data to send back to JavaScript
            status_data.append({
                'id_player': p['id_player'],
                'state': p['state']
            })

        # Convert the list to JSON format for the front-end
        return jsonify(status_data)


    @app.route('/edit/<int:id_player>', methods=['GET', 'POST'])
    @LoggedIn
    def edit_player(id_player):
        """
        Route to edit a player's information.

        On GET: displays a pre-filled form with the current player data.
        On POST: saves the updated values to the database.

        Args:
            id_player (int): The ID of the player to edit.

        Returns:
            GET: HTML page with the edit form.
            POST: Redirect to the devices page after update.
        """

        if request.method == 'POST':
            # FORM SUBMISSION (POST)

            # Retrieve data submitted through the form
            name_place = request.form.get('name_place')
            ip_address = request.form.get('ip_address')
            place_address = request.form.get('place_address')
            place_city = request.form.get('place_city')
            place_postcode = request.form.get('place_postcode')
            place_building_name = request.form.get('place_building_name')
            device_name = request.form.get('device_name')

            # Validate that required fields are not empty
            if not name_place or not ip_address or not place_address:
                return "Error: All required fields must be filled", 400

            # Prepare data for database update
            # Note: DB columns use 'IP_adress' and 'place_adress' (single 'd' – legacy typo in schema)
            form_data = {
                'name_place': name_place,
                'IP_adress': ip_address,
                'place_adress': place_address,
                'place_city': place_city,
                'place_postcode': place_postcode,
                'place_building_name': place_building_name,
                'device_name': device_name
            }

            # Update the player record in the database
            sps.updateDbSongPlayer(form_data, id_player)

            # Redirect back to the referring page (devices list)
            return redirect(request.referrer)

        else:
            # DISPLAY EDIT FORM (GET)

            # Retrieve current player information from the database
            player = sps.findByID(id_player)

            # Return 404 if the player does not exist
            if not player:
                return "Player not found", 404

            available_buildings = sps.findAllBuildingNames()

            # Get the organization ID for the header navigation
            orga = ogs.getIdByName(session.get("organisation_name"))

            # Render the pre-filled edit form
            metadata = {'title': 'Edit Player'}
            context = {
                'metadata': metadata,
                'player': player,
                'orga': orga,
                'buildings': available_buildings
            }
            return render_template('edit_player.html', context=context)

    @app.route('/addPlayer', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def addPlayer():

        if request.method == 'POST':
            # Retrieve form data
            name_place = request.form.get('name_place')
            ip_address = request.form.get('ip_address')
            state = "OFFLINE"  # New devices default to OFFLINE
            place_address = request.form.get('place_address')
            place_city = request.form.get('place_city')
            place_postcode = request.form.get('place_postcode')
            place_building_name = request.form.get('place_building_name')
            device_name = request.form.get('device_name')

            # Get the organization for redirection and device association
            orga_name = session.get('organisation_name')
            orga_id = ogs.getIdByName(orga_name)

            # Create the device in the database
            sps.createDevice(
                name_place,
                ip_address,
                state,
                place_address,
                place_postcode,
                place_city,
                place_building_name,
                device_name,
                orga_id)

            return redirect(url_for('devices', nom_orga=orga_name))

        else:
            # DISPLAY ADD FORM (GET)

            # Get the organization ID for the header navigation
            orga = ogs.getIdByName(session.get('organisation_name'))
            available_buildings = sps.findAllBuildingNames()

            metadata = {'title': 'Add Player'}
            context = {
                'metadata': metadata,
                'orga': orga,
                'buildings': available_buildings
            }
            return render_template('add_player.html', context=context)