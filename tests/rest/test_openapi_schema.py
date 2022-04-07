"""
This module tests return of custom_openapi function
passes in through updated_schema fixture
"""


def test_updated_model_repository(updated_schema):
    """
    Test if an updated summary and description for
    '/v2/repository/index' endpoint is returned by FastAPI
    """
    assert updated_schema['paths']['/v2/repository/index']['post']['summary'] == "Index"
    assert updated_schema['paths']['/v2/repository/index']['post']['description'] == \
        "Index description"


def test_updated_dataplane(updated_schema):
    """
    Test if an updated summary and description for '/v2/health/live' endpoint is
    returned by FastAPI
    """
    assert updated_schema['paths']['/v2/health/live']['get']['description'] == \
        "The “server live” API indicates if the inference server is able " \
        "to receive and respond to metadata and inference requests."
    assert updated_schema['paths']['/v2/health/live']['get']['summary'] == \
        "Server is live"


def test_add_new_endpoint(updated_schema):
    """
    Test if a new endpoint added to dataplane.yaml file is returned by the schema
    """

    assert updated_schema['paths']['/v2/models/{model_name}/ready']\
           == {
      "get": {
        "summary": "Method",
        "operationId": "method_v2_models__model_name__ready_get",
        "parameters": [
          {
            "required": True,
            "schema": {
              "title": "Model Name",
              "type": "string"
            },
            "name": "model_name",
            "in": "path"
          },
          {
            "required": False,
            "schema": {
              "title": "Model Version",
              "type": "string"
            },
            "name": "model_version",
            "in": "query"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    }