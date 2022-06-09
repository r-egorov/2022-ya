import pydantic.schema
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.constants import REF_PREFIX

from yashop.api.schema import ErrorSchema


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="yashop",
        version="1.0.0",
        description="Test task for Yandex backend-development school",
        routes=app.routes,
    )

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if openapi_schema["paths"][path][method]["responses"].get("422"):
                openapi_schema["paths"][path][method]["responses"][
                    "400"
                ] = {
                    "description": "Validation Error",
                    "content": {
                        "application/json": {"schema": {"$ref": f"{REF_PREFIX}ErrorSchema"}}
                    },
                }

                openapi_schema["paths"][path][method]["responses"].pop("422")

    error_response_defs = pydantic.schema.schema(
        (ErrorSchema,), ref_prefix=REF_PREFIX, ref_template=f"{REF_PREFIX}{{model}}"
    )
    openapi_schemas = openapi_schema["components"]["schemas"]
    openapi_schemas.update(error_response_defs["definitions"])
    openapi_schemas.pop("ValidationError")
    openapi_schemas.pop("HTTPValidationError")

    return openapi_schema
