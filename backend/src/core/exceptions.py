from fastapi import HTTPException, status


class ChatbotException(HTTPException):
    def __init__(
        self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(status_code=status_code, detail=detail)


class FileNotFoundError(ChatbotException):
    def __init__(self, detail: str = "File not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class InvalidFileTypeError(ChatbotException):
    def __init__(self, detail: str = "Invalid file type"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class FileTooLargeError(ChatbotException):
    def __init__(self, detail: str = "File too large"):
        super().__init__(
            detail=detail, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )


class SessionNotFoundError(ChatbotException):
    def __init__(self, detail: str = "Session not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)
