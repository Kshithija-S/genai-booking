class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an email that already exists."""
    pass

class DatabaseError(Exception):
    """Raised when there is a database-related error."""
    pass

class AuthenticationError(Exception):
    """Raised when there is an authentication-related error."""
    pass 