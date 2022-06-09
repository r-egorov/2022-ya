from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from yashop.api.schema import ErrorSchema


async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        content=jsonable_encoder(
            ErrorSchema(message=str(exc.detail), code=exc.status_code),
        ),
        status_code=exc.status_code,
    )


async def validation_error_handler(request, exc: RequestValidationError):
    error = ErrorSchema(
        message="Validation failed",
        code=status.HTTP_400_BAD_REQUEST
    )
    return JSONResponse(
        content=error.json(),
        status_code=error.code,
    )

