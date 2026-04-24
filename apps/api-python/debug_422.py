from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import logging

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"422 Error: {exc.errors()}")
    try:
        body = await request.body()
        body_str = body.decode("utf-8")
    except:
        body_str = "could not decode body"
        
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body_str},
    )
