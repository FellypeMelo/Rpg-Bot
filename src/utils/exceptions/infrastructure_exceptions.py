class InfrastructureException(Exception):
    """Base exception for infrastructure-related errors."""
    pass

class DatabaseConnectionError(InfrastructureException):
    """Raised when there's an issue connecting to the database."""
    pass

class RepositoryError(InfrastructureException):
    """Raised when there's an issue with repository operations (e.g., save, get, update, delete)."""
    pass

class CacheError(InfrastructureException):
    """Raised when there's an issue with cache operations."""
    pass