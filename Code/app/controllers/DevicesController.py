from flask import render_template, session, redirect, url_for, request , jsonify
from functools import wraps
import datetime
from app import app
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.UserService import UserService
from app.services.SongPlayerService import SongPlayerService
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService


log = LogService()
sps=SongPlayerService()
ogs=OrganisationService()

class DevicesController :

    @app.route('/devices/<nom_orga>', methods =['GET'])
    @LoggedIn
    def devices(nom_orga):
        
        metadata= {'title': 'Devices'}
        # Get organization ID once to optimize database queries
        id_orga = ogs.getIdByName(nom_orga)

        # Get all players for this organization as a list of dictionaries
        liste_song_player_dict = sps.findAllSongPlayerByOrganisation(id_orga)

        # Retrieve the count of online and offline players for this organization
        nb_on_and_nb_off = sps.countNumberOfSongPlayerOnlineAndOffline(id_orga)
        
        # Unpack counters from the result list/tuple
        nb_on = nb_on_and_nb_off[0]
        nb_off = nb_on_and_nb_off[1]

        return render_template('devices.html', metadata=metadata, liste_song_player=liste_song_player_dict, nb_on=nb_on, nb_off=nb_off, orga=nom_orga)
        

    @app.route('/update/<int:id_player>', methods=['POST','GET'])
    @LoggedIn
    def update(id_player):
    
        # Run the ping test and save the new status (PLAYING/OFFLINE) in the database
        sps.changeState(id_player)

        # Redirect the user back to the previous page to see the updated status
        return redirect(request.referrer)


    @app.route('/delete/<int:id_player>',methods=['POST','GET'])
    @LoggedIn
    @reqrole(['admin'])
    def delete(id_player):

        player= sps.spdao.findByID(id_player)
        log.ldao.createLog(
            "DELETE", 
            f"le lecteur {player.name_place} a été supprimé", 
            datetime.datetime.now(), 
            player.id_orga)
        # Permanently remove the player from the database using the service layer
        sps.deleteSongPlayer(id_player)

        # Stay on the current page to confirm the player is gone from the list
        return redirect(request.referrer)



    #Ici c'est normal qu'il n'y ai pas de GET/POST car cette route ne fait transiter que du JSON 
    #Elle sert a l'auto rafaichisement des statut (c'est une requête AJAX)
    @app.route('/auto_update_status/<nom_orga>') 
    @LoggedIn
    def get_status(nom_orga):
        
        #on recupère l'id de lorganisation
        id_orga = ogs.getIdByName(nom_orga)

        # Récupération de la liste des players de l'organisation
        players = sps.findAllSongPlayerByOrganisation(id_orga)
        status_data = []
    
        for p in players:
            # On déclenche le ping pour chaque player pour mettre à jour la base
            sps.changeState(p['id_player'])
            
            # On prépare les données minimales à envoyer au JavaScript
            status_data.append({
                'id_player': p['id_player'],
                'state': p['state']
            })
    
        # Transformation de la liste en format JSON pour le front-end
        return jsonify(status_data)



# ici y manque juste la logique pour ajouter un device est cette page seras fini  
    @app.route('/edit/<int:id_player>', methods=['GET', 'POST'])
    @LoggedIn
    def edit_player(id_player):
        """
        Route pour modifier les informations d'un lecteur
        
        EXPLICATION mes loulous que j'aime:
        
        Cette route permet à un utilisateur connecté de modifier les infos d'un lecteur.
        
        Comment ça marche en bien gui , putain le senegal a fait match nul?
        1. L'utilisateur clique sur "Modifier" dans devices.html
        2. GET /edit/123 → On affiche un formulaire pré-rempli avec les données actuelles
        3. L'utilisateur modifie les champs qu'il veut
        4. POST /edit/123 → On enregistre les nouvelles valeurs dans la BDD
        5. Redirection vers la page devices pour voir le résultat
        
        Paramètres:
            id_player (int): L'ID du lecteur à modifier
        
        Retourne:
            - Si GET : Page HTML avec formulaire d'édition
            - Si POST : Redirection vers la page devices après modification
        """
        
        if request.method == 'POST':
            #  TRAITEMENT DU FORMULAIRE (POST)
            
            # Récupération des données envoyées par le formulaire
            # request.form contient tout ce que l'utilisateur a tapé
            name_place = request.form.get('name_place')
            ip_address = request.form.get('ip_address')
            place_address = request.form.get('place_address')
            place_city = request.form.get('place_city')
            place_postcode = request.form.get('place_postcode')
            place_building_name = request.form.get('place_building_name')
            device_name = request.form.get('device_name')
            
            # Vérification que tous les champs sont remplis
            # Si un champ est vide (None ou ""), on retourne une erreur
            if not name_place or not ip_address or not place_address:
                return "Erreur : Tous les champs sont obligatoires", 400
            
            # Préparation des données pour la mise à jour
            # ATTENTION : Dans la BDD c'est IP_adress et place_adress (avec 1 seul d, donc belek faut modifier)
            # C'est une faute de frappe dans le schema.sql mais on doit utiliser ces noms
            form_data = {
                'name_place': name_place,
                'IP_adress': ip_address,      # ← Attention à l'orthographe
                'address_place': place_address,  # ← Attention à l'orthographe
                'city_place': place_city,
                'postcode_place': place_postcode,
                'building_name_place': place_building_name,
                'device_name': device_name
            }
            
            # Appel du service pour mettre à jour dans la base de données
            # sps = SongPlayerService (défini en haut du fichier)
            # sps.spdao = SongPlayerDAO (le DAO qui parle à la BDD)
            # updateDbSongPlayer() va faire un UPDATE SQL
            sps.spdao.updateDbSongPlayer(form_data, id_player)
            
            # Redirection vers la page d'où on vient (devices)
            # request.referrer contient l'URL de la page précédente
            return redirect(request.referrer)
        
        else:
            #  AFFICHAGE DU FORMULAIRE (GET) 
            
            # Récupération des informations actuelles du lecteur
            # On cherche dans la BDD avec l'ID
            player = sps.spdao.findByID(id_player)
            
            # Si le lecteur n'existe pas dans la BDD
            if not player:
                return "Lecteur non trouvé", 404
            
            available_buildings = sps.spdao.findAllBuildingNames()

            # Récupération du nom de l'organisation pour le header
            # player.id_orga contient l'ID de l'organisation
            orga = ogs.getIdByName(session.get("organisation_name"))  # On va chercher le nom
            
            # Affichage du formulaire pré-rempli
            metadata = {'title': 'Modifier Lecteur'}
            return render_template('edit_player.html',
                                 metadata=metadata,
                                 player=player,
                                 orga=orga,
                                 buildings=available_buildings)  # Pour le header
    
    @app.route('/addPlayer', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def addPlayer():
        
        if request.method == 'POST':
            # Récupération des données du formulaire
            name_place = request.form.get('name_place')
            ip_address = request.form.get('ip_address')
            state =  "OFFLINE"  # Par défaut, le nouvel appareil est hors ligne
            #last_synchronization = ... obtenir la date actuelle => fais dans le DAO en PostgreSQL avec CURRENT_TIMESTAMP
            place_address = request.form.get('place_address')
            place_city = request.form.get('place_city')
            place_postcode = request.form.get('place_postcode')
            place_building_name = request.form.get('place_building_name')
            device_name = request.form.get('device_name')

            # Récupérer l'organisation pour redirection et association au nouveau device
            orga_name = session.get('organisation_name')

            orga_id = ogs.getIdByName(orga_name)
            
            # Création du device
            sps.spdao.createDevice(
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
            #  AFFICHAGE DU FORMULAIRE (GET) 
            
            # Récupération du nom de l'organisation pour le header
            # player.id_orga contient l'ID de l'organisation
            orga = ogs.getIdByName(session.get('organisation_name'))  # On va chercher l'id de l'organisation
            available_buildings = sps.spdao.findAllBuildingNames()
            # Affichage du formulaire pré-rempli
            metadata = {'title': 'Ajouter Lecteur'}
            return render_template('add_player.html',
                                metadata=metadata,
                                orga=orga,
                                buildings=available_buildings)  # Pour le header