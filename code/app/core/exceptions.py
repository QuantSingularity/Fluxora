class FluxoraError(Exception):
    """Base exception class for all project-specific errors."""


class DataValidationError(FluxoraError):
    """Raised when data fails quality checks."""


class ModelServicingError(FluxoraError):
    """Raised when model serving fails."""


class FeatureStoreConnectionError(FluxoraError):
    """Raised when unable to connect to feature store."""


class TemporalCoherenceError(FluxoraError):
    """Raised when time series data has gaps/inconsistencies."""


class ResourceNotFoundError(FluxoraError):
    """Raised when a requested resource cannot be found."""


class AuthenticationError(FluxoraError):
    """Raised when authentication fails."""


class AuthorizationError(FluxoraError):
    """Raised when authorization fails."""
