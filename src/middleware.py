# src/middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(level=logging.INFO)


# Middleware для обработки IntegrityError
async def db_integrity_error_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except IntegrityError as e:
        if "unique constraint" in str(e.orig):
            return JSONResponse(
                status_code=400,
                content={"detail": "Unique constraint violation, likely a duplicate entry."}
            )
        return JSONResponse(
            status_code=400,
            content={"detail": "Integrity error occurred."}
        )


# Middleware для обработки валидации
async def validation_exception_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except RequestValidationError as exc:
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body},
        )


# Middleware для обработки ошибок 500
async def internal_server_error_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."}
        )


# Middleware для обработки ошибок 404
async def not_found_error_middleware(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"detail": "Resource not found."}
        )
    return response
