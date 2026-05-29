import sqlite3
import os
import bcrypt
from datetime import datetime, timedelta

# Récupère le dossier où se trouve le fichier initdb.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construit les chemins complets
DB_PATH = os.path.join(BASE_DIR, 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

# Connexion
conn = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH) as f:
    conn.executescript(f.read())


def populate_database():
    print("--- Démarrage de l'insertion des données ---")

    # Roles
    roles = [
        ('admin',     'Administrator of the web app'),
        ('marketing', 'They create the base of the playlists and fix it to week days'),
        ('sales',     'They manage the song player and the messages to insert in the playlists')
    ]
    conn.executemany("INSERT INTO role (role, description) VALUES (?, ?)", roles)
    print("✅ Roles insérés.")

    # Types de fichiers
    conn.executemany("INSERT INTO type_file (type_file) VALUES (?)", [('mp3',)])
    print("✅ Types insérés.")

    # ✅ CORRECTION : mot de passe + email pour chaque utilisateur
    # L'admin par défaut est créé ici avec des identifiants connus
    password_clair = '12345'
    hashed_pw = bcrypt.hashpw(password_clair.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    users = [
        # (username,  role,        password,   email)
        ("admin",     'admin',     hashed_pw,  'admin@soundstream.local'),     # ← ADMIN PAR DÉFAUT
        ("Romain",   'admin',     hashed_pw,  'romain@soundstream.local'),
        ("Tristan",  'marketing', hashed_pw,  'tristan@soundstream.local'),
        ("Abou",     'sales',     hashed_pw,  'abou@soundstream.local'),
    ]
    conn.executemany(
        "INSERT INTO user_ (username, role, password, email) VALUES (?, ?, ?, ?)",
        users
    )
    print("✅ Utilisateurs insérés.")
    print("   → Admin par défaut : username='admin'  password='12345'")
    print("   ⚠️  Changez ce mot de passe dès la première connexion !")

    # Organisations
    orgas = [('Orga1',), ('Orga2',), ('Orga3',)]
    conn.executemany("INSERT INTO organisation (name_orga) VALUES (?)", orgas)

    # work_link : (id_user, id_orga)
    # user ids : admin=1, Romain=2, Tristan=3, Abou=4
    links = [
        (1, 1),        # admin  → Orga1
        (2, 1), (2, 2),
        (3, 2), (3, 3),
        (4, 2), (4, 3),
    ]
    conn.executemany("INSERT INTO work_link (id_user, id_orga) VALUES (?, ?)", links)
    print("✅ Orgas & Links insérés.")

    # Planning
    days = [('Monday',), ('Tuesday',), ('Wednesday',), ('Thursday',),
            ('Friday',), ('Saturday',), ('Sunday',)]
    conn.executemany("INSERT INTO Planning (day_) VALUES (?)", days)
    print("✅ Planning inséré.")

    # Song player
    now = datetime.now()
    players = [
        ('Abou', '10.100.27.134', 'OFFLINE', now,
         '12 Rue de Rivoli', '75000', 'Paris',
         'centre commercial', 'aboubakry', 2),
    ]
    conn.executemany(
        "INSERT INTO song_player "
        "(name_place, IP_adress, state, last_synchronization, "
        " place_adress, place_postcode, place_city, "
        " place_building_name, device_name, id_orga) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        players
    )
    print("✅ Players insérés.")

    conn.commit()
    print("--- Base de données prête ! ---")


populate_database()
conn.close()