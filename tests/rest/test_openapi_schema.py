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
    Test if a description and summary for a new endpoint added to dataplane.yaml
    are returned by FastAPI
    """
    assert updated_schema['paths']['/v2/models/{model_name}/ready'][
        'get']['description'] == "The “model ready” health API indicates " \
        "if a specific model is ready for inferencing. " \
        "The model name and (optionally) " \
        "version must be available in the URL. " \
        "If a version is not provided the server may " \
        "choose a version based on its own policies."

    assert updated_schema['paths']['/v2/models/{model_name}/ready']['get'][
        'summary'] == "Model Ready"
