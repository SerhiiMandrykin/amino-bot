class WrongPassword(Exception):
    pass


class WrongEmail(Exception):
    pass


class RequestedApproval(Exception):
    pass


class UserBlocked(Exception):
    pass


class DisabledInviting(Exception):
    pass


class UnexpectedException(Exception):
    pass


class NoDialogflowCredentialsFileFound(Exception):
    pass
