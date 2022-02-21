import uvicorn

from ..settings import Settings
from ..handlers import DataPlane, ModelRepositoryHandlers, get_custom_handlers, get_schema
from ..model import MLModel

from .utils import matches
from .app import create_app
from fastapi.openapi.utils import get_openapi
from ..logging import logger


class _NoSignalServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass


class RESTServer:
    def __init__(
        self,
        settings: Settings,
        data_plane: DataPlane,
        model_repository_handlers: ModelRepositoryHandlers,
    ):
        self._settings = settings
        self._data_plane = data_plane
        self._model_repository_handlers = model_repository_handlers
        self._app = create_app(
            self._settings,
            data_plane=self._data_plane,
            model_repository_handlers=self._model_repository_handlers,
        )
        self._app.openapi = self.custom_openapi

    def custom_openapi(self):
        endpoints = get_schema()
        if self._app.openapi_schema:
            return self._app.openapi_schema
        openapi_schema = get_openapi(title="MLServer APIs", version="1.0", description="", routes=self._app.routes, )
        for path in openapi_schema['paths']:
            for i in range(len(endpoints)):
                endpoint = endpoints[i]
                if path == endpoint["path"]:
                    operation = endpoint["operation"]
                    desc = endpoint["desc"]
                    summary = endpoint["summary"]
                    openapi_schema['paths'][path][operation]['description'] = desc
                    openapi_schema['paths'][path][operation]['summary'] = summary

        self._app.openapi_schema = openapi_schema
        return self._app.openapi_schema

    async def add_custom_handlers(self, model: MLModel):
        handlers = get_custom_handlers(model)
        for custom_handler, handler_method in handlers:
            self._app.add_api_route(
                custom_handler.rest_path,
                handler_method,
                methods=[custom_handler.rest_method],
            )

    async def delete_custom_handlers(self, model: MLModel):
        handlers = get_custom_handlers(model)
        if len(handlers) == 0:
            return

        # NOTE: Loop in reverse, so that it's quicker to find all the recently
        # added routes and we can remove routes on-the-fly
        for i, route in reversed(list(enumerate(self._app.routes))):
            for j, (custom_handler, handler_method) in enumerate(handlers):
                if matches(route, custom_handler, handler_method):  # type: ignore
                    self._app.routes.pop(i)
                    handlers.pop(j)

    async def start(self):
        cfg = uvicorn.Config(
            self._app, host=self._settings.host, port=self._settings.http_port
        )
        self._server = _NoSignalServer(cfg)
        await self._server.serve()

    async def stop(self):
        self._server.handle_exit(sig=None, frame=None)
