from typing import Callable
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import Response as FastAPIResponse
from fastapi.routing import APIRoute as FastAPIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette_exporter import PrometheusMiddleware, handle_metrics
from .endpoints import Endpoints, ModelRepositoryEndpoints
from .requests import Request
from .responses import Response
from .errors import _EXCEPTION_HANDLERS
from ..settings import Settings
from ..handlers import DataPlane, ModelRepositoryHandlers


class APIRoute(FastAPIRoute):
    """
    Custom route to use our own Request handler.
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> FastAPIResponse:
            request = Request(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


def create_app(
    settings: Settings,
    data_plane: DataPlane,
    model_repository_handlers: ModelRepositoryHandlers,
) -> FastAPI:
    endpoints = Endpoints(data_plane)
    model_repository_endpoints = ModelRepositoryEndpoints(model_repository_handlers)

    routes = [
        # Model ready
        APIRoute(
            "/v2/models/{model_name}/ready",
            endpoints.model_ready,
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}/ready",
            endpoints.model_ready,
        ),
        # Model infer
        APIRoute(
            "/v2/models/{model_name}/infer",
            endpoints.infer,
            methods=["POST"],
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}/infer",
            endpoints.infer,
            methods=["POST"],
        ),
        # Model metadata
        APIRoute(
            "/v2/models/{model_name}",
            endpoints.model_metadata,
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}",
            endpoints.model_metadata,
        ),
        # Liveness and readiness
        APIRoute("/v2/health/live", endpoints.live),
        APIRoute("/v2/health/ready", endpoints.ready),
        # Server metadata
        APIRoute(
            "/v2",
            endpoints.metadata,
        ),
    ]

    routes += [
        # Model Repository API
        APIRoute(
            "/v2/repository/index",
            model_repository_endpoints.index,
            methods=["POST"],
        ),
        APIRoute(
            "/v2/repository/models/{model_name}/load",
            model_repository_endpoints.load,
            methods=["POST"],
        ),
        APIRoute(
            "/v2/repository/models/{model_name}/unload",
            model_repository_endpoints.unload,
            methods=["POST"],
        ),
    ]

    app = FastAPI(
        debug=settings.debug,
        routes=routes,  # type: ignore
        default_response_class=Response,
        exception_handlers=_EXCEPTION_HANDLERS,  # type: ignore
    )

    if settings.cors_settings is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_settings.allow_origins,
            allow_origin_regex=settings.cors_settings.allow_origin_regex,
            allow_credentials=settings.cors_settings.allow_credentials,
            allow_methods=settings.cors_settings.allow_methods,
            allow_headers=settings.cors_settings.allow_headers,
            max_age=settings.cors_settings.max_age,
        )

    if settings.metrics_endpoint:
        app.add_middleware(
            PrometheusMiddleware,
            app_name="mlserver",
            prefix="rest_server",
            # TODO: Should we also exclude model's health endpoints?
            skip_paths=[
                settings.metrics_endpoint,
                "/v2/health/live",
                "/v2/health/ready",
            ],
        )
        app.add_route(settings.metrics_endpoint, handle_metrics)

    return app


def custom_openapi(app: FastAPI, input_schema: Dict) -> Dict[str, Any]:
    """
    Method used to extend openapi schema with the contents of dataplane.yaml and
    model_repository.yaml files. The method takes in two parameters instance of FastAPI
    and input schema dictionary from which contents are extracted
    """
    validation_error = {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }

    openapi_schema = get_openapi(title=input_schema['info']['title'],
                                 version=input_schema['info']['version'],
                                 description="", openapi_version='3.0.2',
                                 routes=app.routes, )

    openapi_schema = data_merge(openapi_schema, input_schema)


    """
    for path, spec in input_schema['paths'].items():
        if path in openapi_schema['paths']:
            spec_orig = openapi_schema['paths'][path]
            openapi_schema['paths'][path] = spec

            # TODO: ask if should merge or recreate
            # validation error
            if {'parameters', 'get'} == \
                    set(openapi_schema['paths'][path].keys()):
                openapi_schema['paths'][path]['get']['responses']['422'] = \
                    validation_error
            elif 'post' in openapi_schema['paths'][path].keys():
                openapi_schema['paths'][path]['post']['responses']['422'] = \
                    validation_error

    for input_schema_key, input_schema_value in \
            input_schema['components']['schemas'].items():
        for openapi_schema_key, _ \
                in list(openapi_schema['components']['schemas'].items()):
            if input_schema_key == openapi_schema_key:
                openapi_schema['components']['schemas'][openapi_schema_key] = \
                    input_schema_value
            else:
                openapi_schema['components']['schemas'][input_schema_key] = \
                    input_schema_value
    
    """
    print(openapi_schema)
    app.openapi_schema = openapi_schema

    return app.openapi_schema


class YamlReaderError(Exception):
    pass


def data_merge(openapi_schema, input_schema):
    key = None


    if openapi_schema is None or isinstance(openapi_schema, str):
        # border case for first run or if a is a primitive
        #print("--------------------")
        #print(openapi_schema)
        openapi_schema = input_schema
        #print(openapi_schema)
    elif isinstance(openapi_schema, list):
        # lists can be only appended
        #test
        #print("--------------------")
        #print(openapi_schema)
        if isinstance(input_schema, list):
            # merge lists
           # print('If')
            openapi_schema.extend(input_schema)
            #print(openapi_schema)
        else:
            # append to list
            #print('Else')
            openapi_schema.append(input_schema)
            #print(openapi_schema)
    elif isinstance(openapi_schema, dict):
        # dicts must be merged
        if isinstance(input_schema, dict):
            for key in input_schema:
                if key in openapi_schema:
                    openapi_schema[key] = data_merge(openapi_schema[key], input_schema[key])
                else:
                    openapi_schema[key] = input_schema[key]

    return openapi_schema
