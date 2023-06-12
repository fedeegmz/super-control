from fastapi import HTTPException, status

class HTTPError:
    def __init__(self) -> None:
        self.status_code = None
        self.detail = None
        self.error = None

    def save_err(self, status_code: int, message: str, err: str = None) -> None:
        detail = {
            "errmsg": message
        }
        if err:
            detail["err"] = err

        self.status_code = status_code
        self.detail = detail

        self.error = HTTPException(
            status_code = self.status_code,
            detail = self.detail
        )


    def conflict(self, message: str, err: str = None) -> HTTPException:
        self.save_err(
            status_code = status.HTTP_409_CONFLICT,
            message = message,
            err = err
        )

        return self.error
    
    def not_found(self, message: str, err: str = None) -> HTTPException:
        self.save_err(
            status_code = status.HTTP_404_NOT_FOUND,
            message = message,
            err = err
        )
        
        return self.error
    
    def bad_request(self, message: str, err: str = None) -> HTTPException:
        self.save_err(
            status_code = status.HTTP_400_BAD_REQUEST,
            message = message,
            err = err
        )

        return self.error