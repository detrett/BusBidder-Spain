# Defining custom errors that the rest of the application can recognize
class DataLoadError(Exception):
    """Raised when a source CSV cannot be loaded correctly."""

class DataValidationError(Exception):
    """Raised when a data record fails validation."""