from app.models.UserDAO import UserDAO

class UserService():

    def __init__(self):
		# cette ligne utilise le Data Access Object (DAO) dédié aux fichier JSON
        self.udao = UserDAO()
    
    def findUsersInOrganisation(self, organisation):
        """ Get all the users of an organisation """
        return self.udao.findUsersInOrganisation(organisation)
    
    def deleteByUsername(self, username):
        """ Delete user by username """
        return self.udao.deleteByUsername(username)
    
    def findByUsername(self, username):
        """ Get user by username  """
        return self.udao.findByUsername(username)
    
    def findAllUsername(self) -> list[str]:
        """ Get all usernames """
        return self.udao.findAllUsername()


    def findByEmail(self, email):
        """Get user by email"""
        return self.udao.findByEmail(email)

    def updateEmail(self, username, email):
        """Update user email"""
        return self.udao.updateEmail(username, email)

    def changePassword(self, username, password):
        """Change user password"""
        return self.udao.changePassword(username, password)
    