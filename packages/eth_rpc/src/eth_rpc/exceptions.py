class LogResponseExceededError(Exception):
    message: str
    recommended_start: int
    recommended_end: int

    def __init__(self, message, recommended_start: int, recommended_end: int):
        self.message = message
        super().__init__(message)
        self.recommended_start = recommended_start
        self.recommended_end = recommended_end


class LogDecodeError(ValueError): ...


class RateLimitingError(ValueError): ...


class RPCDecodeError(ValueError): ...


class UnsupportedChainIDException(ValueError): ...
