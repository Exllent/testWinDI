from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class CustomException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsException(CustomException):
    pass


class InvalidCredentials(CustomException):
    pass


class ChatAlreadyExistsException(CustomException):
    pass


class InternalServerErrorException(CustomException):
    pass


class ChatNotFoundException(CustomException):
    pass


class MessageNotFoundException(CustomException):
    pass


class ChatOwnerException(CustomException):
    pass


class CreateMessageException(CustomException):
    pass


class UpdateMessageException(CustomException):
    pass


class CreateBalkMessageException(CustomException):
    pass


class MessageAlreadyReadException(CustomException):
    pass


class PermissionDeniedException(CustomException):
    pass
