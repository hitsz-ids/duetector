from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


class NotFoundError(HTTPException):
    def __init__(self, what: str = ""):
        if what:
            what = f"{what} "
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=f"{what}Not found")
