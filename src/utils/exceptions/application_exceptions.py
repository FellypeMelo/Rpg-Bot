class ApplicationException(Exception):
    """Base exception for application-level errors."""
    pass

class CharacterError(ApplicationException):
    """Raised when there's an issue with character-related operations."""
    pass

class CharacterNotFoundError(CharacterError):
    """Raised when a character is not found."""
    pass

class InvalidCharacterError(CharacterError):
    """Raised when an operation is attempted on a character that is not valid for the context (e.g., wrong owner)."""
    pass

class InvalidInputError(ApplicationException):
    """Raised when input validation fails."""
    pass

class LevelUpError(ApplicationException):
    """Raised when there's an issue with leveling up a character."""
    pass

class CombatError(ApplicationException):
    """Raised when there's an issue with combat-related operations."""
    pass

class CombatSessionNotFoundError(CombatError):
    """Raised when a combat session is not found."""
    pass

class MaxCombatSessionsError(CombatError):
    """Raised when a user tries to start more than the allowed number of combat sessions."""
    pass

class PlayerPreferencesError(ApplicationException):
    """Raised when there's an issue with player preferences operations."""
    pass

class AppPermissionError(ApplicationException):
    """Raised when a user does not have permission to perform an action."""
    pass