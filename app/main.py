from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    http_exception_handler,
    general_exception_handler,
)


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    from fastapi.exceptions import RequestValidationError
    from app.core.exceptions import validation_exception_handler
    
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, general_exception_handler)
    
    # Include API routers
    from app.api import api_router
    application.include_router(api_router, prefix="/api")
    
    # Include GraphQL router
    from app.graphql import graphql_router
    application.include_router(graphql_router, prefix="/graphql")
    
    return application


# Create the application instance
app = create_application()


@app.get("/", tags=["health"])
async def root() -> dict:
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "healthy",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "healthy"}
