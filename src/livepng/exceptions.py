class WrongFormatException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoFolderInspectedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidModelException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NotLoadedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
