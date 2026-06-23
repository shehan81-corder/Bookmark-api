from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.db import models
from app.api import auth, bookmarks

app = FastAPI(title="Bookmarks API")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(
    bookmarks.router, prefix="/api/bookmarks", tags=["bookmarks"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Bookmarks API",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
