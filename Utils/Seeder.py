import sqlite3
import os
import bcrypt
from datetime import datetime

# Get the directory where initdb.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the complete paths
DB_PATH = os.path.join(BASE_DIR, 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

# Database Connection
conn = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH) as f:
    conn.executescript(f.read())


### DEBUG FUNCTION ###
# /!\ TO DELETE AFTER THE SITE IS BUILT #

def populate_database():
    print("--- Starting dummy data insertion ---")

    print("Specify which data do you want to insert. All [True/False]: ")
    selection = input()
    if selection.lower() == 'true':
        insert_roles()
        insert_types()
        insert_users()
        insert_orgas()
        insert_planning()
    else :
        if input('insert roles? [True/False]: ').lower() == 'true':
            insert_roles()
        if input('insert types? [True/False]: ').lower() == 'true':
            insert_types()
        if input('insert users? [True/False]: ').lower() == 'true':
            insert_users()
        if input('insert orgas? [True/False]: ').lower() == 'true':
            insert_orgas()
        if input('insert planning? [True/False]: ').lower() == 'true':
            insert_planning()

    conn.commit()


def insert_roles():
    # Initialization of roles
    roles = [
        ('admin', 'Administrator of the web app'),
        ('marketing', 'they create the base of the playlists and fix it to week days'),
        ('sales', 'they manage the song player and the messages to insert in the playlists')
    ]

    conn.executemany("INSERT INTO role (role, description) VALUES (?, ?)", roles)
    print("✅ Roles inserted.")

def insert_types():
    # Initialization of types
    type_file = [
        ('mp3',)
    ]

    conn.executemany("INSERT INTO type_file (type_file) VALUES (?)", type_file)
    print("✅ Types inserted.")

def insert_users():
    # Initialization of users
    users_name = ['Romain', 'Tristan', 'Abou']
    user_role = ['admin', 'marketing', 'sales']
    passwords_clair = ['12345', '678910', '1112131415']

    users = []
    for name, role, pw in zip(users_name, user_role, passwords_clair):
        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        users.append((name, role, hashed_pw))

    conn.executemany("INSERT INTO user_ (username, role, password) VALUES (?, ?, ?)", users)
    print("✅ Users inserted.")

def insert_orgas():
    # Initialization of organisations
    orgas = [
        ('Orga1',),
        ('Orga2',),
        ('Orga3',),
    ]
    conn.executemany("INSERT INTO organisation (name_orga) VALUES (?)", orgas)

    links = [
        (1, 1), (1, 2),
        (2, 2), (2, 3),
        (3, 2), (3, 3)
    ]
    conn.executemany("INSERT INTO work_link (id_user, id_orga) VALUES (?, ?)", links)
    print("✅ Orgas & Links inserted.")

def insert_planning():
    # Initialization of planning
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 3. PLANNING (Jours de la semaine)
    days = [('Monday',), ('Tuesday',), ('Wednesday',), ('Thursday',), ('Friday',), ('Saturday',), ('Sunday',)]
    conn.executemany("INSERT INTO Planning (day_) VALUES (?)", days)
    print("✅ Planning inserted.")

    # 6. SONG_PLAYER (Les boitiers physiques)
    players = [
        ('Abou', '10.100.27.134', 'OFFLINE', now_str, '12 Rue de Rivoli','75000', 'Paris', 'centre commercial', 'aboubakry', 2), # JBL
    ]
    conn.executemany("INSERT INTO song_player (name_place, IP_adress, state, last_synchronization, place_adress, place_postcode, place_city, place_building_name, device_name, id_orga) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", players)
    print("✅ Players inserted.")

# Execution
try:
    populate_database()
finally:
    conn.close()

