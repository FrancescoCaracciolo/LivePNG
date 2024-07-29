class WrongFormatException(Exception):
    """If a model is in the wrong format"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoFolderInspectedException(Exception):
    """If no folder has been inspected yet"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidModelException(Exception):
    """If the given model is not valid"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NotLoadedException(Exception):
    """If the model has not been loaded yet"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NotFoundException(Exception):
    """If something was not found"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
