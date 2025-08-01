class CustomException(Exception):

    def __init__(self, message="Something went wrong", status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        return {
            "message": self.message,
            "status_code": self.status_code,
            "payload": self.payload,
        }
