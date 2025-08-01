class UserAlreadyExistsError(Exception):
    pass


class UserDoesNotExistError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class UnAuthorizedUserError(Exception):
    pass
