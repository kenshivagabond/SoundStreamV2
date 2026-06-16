from app.models.UserDAO import UserDAO

class UserService():

    def __init__(self):
        # Data Access Object for user database operations
        self.udao = UserDAO()

    def findUsersInOrganisation(self, organisation):
        """ Get all the users of an organisation """
        return self.udao.findUsersInOrganisation(organisation)

    def deleteByUsername(self, username):
        """ Delete user by username """
        return self.udao.deleteByUsername(username)

    def findByUsername(self, username):
        """ Get user by username """
        return self.udao.findByUsername(username)

    def findAllUsername(self) -> list[str]:
        """ Get all usernames """
        return self.udao.findAllUsername()

    def getOrganisationByUsername(self, username: str) -> str:
        """ Get the organisation of a user by username. """
        return self.udao.getOrganisationByUsername(username)

    def getAllRoles(self) -> list:
        """ Get all available roles from the role table """
        return self.udao.getAllRoles()

    def changePassword(self, username, password) -> None:
        """ Change the password of the user """
        self.udao.changePassword(username, password)

    def updateUserRole(self, username, new_role) -> None:
        """ Update user role """
        self.udao.updateUserRole(username, new_role)

    def createUser(self, username, password, role, organisation) -> None:
        """ Create a new user and link them to an organisation """
        self.udao.createUser(username, password, role, organisation)

    def findAll(self) -> list:
        """ Get all users """
        return self.udao.findAll()