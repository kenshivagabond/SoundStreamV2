import sqlite3
from app import app
from app.models.User import User
from app.models.UserDAOInterface import UserDAOInterface

import bcrypt

class UserDAO(UserDAOInterface) :
    
    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'
    
    def _getDbConnection(self):
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def _generatePWDHash(self, password) -> str:
        """ Generate password hash from plain text password """
        password_bytes = password.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        password_hashed = hashed_bytes.decode('utf-8')
        return password_hashed
    
    def createUser(self, username, password, role, organisation) -> None:
        """ create a new user """
        if username in self.findUsersInOrganisation(organisation):
            raise ValueError("Username already exists")
        
        conn  = self._getDbConnection()
        hashed_password = self._generatePWDHash(password)
        query = 'INSERT INTO user_(username, password, role) VALUES (?,?,?)'
        conn.execute(query, (username,hashed_password,role))

        conn.commit()
        conn.close()

        self.createLinkUserOrganisation(username, organisation)

    def createLinkUserOrganisation(self, username, organisation) -> None:
        """ Create a link between a user and an organisation """
        conn  = self._getDbConnection()

        query_idUser = """
            SELECT u.id_user
            FROM user_ u
            WHERE u.username = ?
        """
        user_id = conn.execute(query_idUser, (username,)).fetchone()[0]
        conn.commit()
        conn.close()

        conn  = self._getDbConnection()
        query_idOrga = """
            SELECT o.id_orga
            FROM organisation o
            WHERE o.name_orga = ?
        """
        orga_id = conn.execute(query_idOrga, (organisation,)).fetchone()[0]
        conn.commit()
        conn.close()

        conn  = self._getDbConnection()
        links = (user_id, orga_id)
        conn.execute("INSERT INTO work_link (id_user, id_orga) VALUES (?, ?)", links)

        conn.commit()
        conn.close()
        
    def findByUsername(self, username) -> User:
        """ Get user by username """
        conn = self._getDbConnection()
        res = conn.execute('SELECT * FROM user_ WHERE username = ?', (username,)).fetchone()
        conn.close()

        if res:
            return User(dict(res))
        return None
    
    def findUsersInOrganisation(self, organisation) -> list[str]:
        """ Get all the users of an organisation """
        conn = self._getDbConnection()
        query = """
            SELECT u.username
            FROM user_ u
            JOIN work_link w ON u.id_user = w.id_user
            JOIN organisation o ON w.id_orga = o.id_orga
            WHERE o.name_orga = ?
        """
        res = conn.execute(query, (organisation,)).fetchall()
        conn.close()
        return [row[0] for row in res]

    def verifyUser(self,username, password) -> bool:
        """Verify if username and password are correct"""
        user = self.findByUsername(username)

        if user is None:
            return False
        
        #Check password using bcrypt 
        hashed_pw = user.password.encode('utf-8')
        input_pw = password.encode('utf-8')

        return bcrypt.checkpw(input_pw, hashed_pw)
    
    def changePassword(self, username, password) -> None:
        """Change the password of the user"""
        conn = self._getDbConnection()

        #Hash the new password
        hashed_password = self._generatePWDHash(password)

        #update the password
        query = 'UPDATE user_ SET password = ? WHERE username = ?'
        conn.execute(query, (hashed_password, username))
        conn.commit()
        conn.close()

    def deleteByUsername(self,username) -> None:
        """ Delete a user by username""" 
        conn = self._getDbConnection()

        # Delete the work_link entries first
        query = 'DELETE FROM work_link WHERE id_user = (SELECT id_user FROM user_ WHERE username = ?)'
        conn.execute(query,(username,))
        conn.commit()

        # Delete the user 
        query = 'DELETE FROM user_ WHERE username = ?'
        conn.execute(query,(username,))
        conn.commit()
        conn.close()

    def updateUserRole(self, username, new_role) -> None:
        """Update user role"""
        conn = self._getDbConnection()
        query = 'UPDATE user_ SET role = ? WHERE username = ?'
        conn.execute(query, (new_role, username))
        conn.commit()
        conn.close()

    def getOrganisationByUsername(self, username) -> str:
        """Get the organisation name of a user"""
        conn = self._getDbConnection()
        query = """
            SELECT o.name_orga 
            FROM organisation o
            JOIN work_link w ON o.id_orga = w.id_orga
            JOIN user_ u ON w.id_user = u.id_user
            WHERE u.username = ?
        """
        result = conn.execute(query, (username,)).fetchone()
        conn.close()
    
        return result[0] if result else None

    def getAllRoles(self) -> list:
        """Get all available roles from the role table"""
        conn = self._getDbConnection()
        query = 'SELECT role FROM role'
        results = conn.execute(query).fetchall()
        conn.close()
        return [row[0] for row in results]

    def findAll(self) -> list[User]:
        """ Get all users """
        conn = self._getDbConnection()
        users = conn.execute('SELECT * FROM user_ ;').fetchall()
        userList = list()
        for user in users : 
            userList.append(User(dict(user)))
        conn.close()
        return userList
    
    def findAllUsername(self) -> list[str]:
        """ Get all usernames """
        conn = self._getDbConnection()
        users = conn.execute('SELECT username FROM user_ ;').fetchall()
        usernameList = list()
        for user in users : 
            usernameList.append(user['username'])
        conn.close()
        return usernameList