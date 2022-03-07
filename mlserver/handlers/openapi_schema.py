"""
This module processes openapi schema yaml files in order
to retrieve descriptions and summaries of endpoints
"""
import re
from typing import List, Dict
import yaml


def process_schema(input_schema: Dict) -> List[Dict[str, str]]:
    """
    Method used to extract API paths and corresponding descriptions and summaries.
    Takes in as a parameter openapi schema, represented as a dictionary object.
    Returns list of objects, where each object includes an API path, operation and
    if available summary and a description of an API
    """

    endpoints = []

    # get API paths
    for path in input_schema['paths']:
        path_node = input_schema['paths'][path]
        # operations supported by openapi 3.0
        operations = ["get", "post", "put", "patch",
                      "delete", "head", "options", "trace"]
        for operation in path_node:
            if operation in operations:
                endpoint = {"path": normalize_paths(path),
                            "operation": operation}
                if 'description' in input_schema['paths'][path][operation]:
                    endpoint["desc"] = \
                        input_schema['paths'][path][operation]['description']
                if 'summary' in input_schema['paths'][path][operation]:
                    endpoint["summary"] = \
                        input_schema['paths'][path][operation]['summary']

                endpoints.append(endpoint)

    return endpoints


def normalize_paths(path: str):
    """
        Method used to normalize API paths in yaml files to match MLServer API paths
    """
    path_elements = [{"to_replace": r'\$\{MODEL_NAME\}',
                      "replacement": "{model_name}"},
                     {"to_replace": r'\$\{MODEL_VERSION\}',
                      "replacement": "{model_version}"},
                     {"to_replace": r'/v2/$',
                      "replacement": "/v2"}]

    for element in path_elements:
        path = re.sub(element["to_replace"], element["replacement"], path)

    return path


def merge_schemas(path_1: str, path_2: str) -> Dict[str, str]:
    """
        Method used to merge API paths and schemas of two openapi yaml files.
        The paths are taken in as parameters.
        It returns a dictionary of merged schemas.
    """
    with open(path_1, encoding='utf-8') as file:
        schema_1 = yaml.load(file, Loader=yaml.FullLoader)

    with open(path_2, encoding='utf-8') as file:
        schema_2 = yaml.load(file, Loader=yaml.FullLoader)

    merged_schema = schema_1.copy()
    merged_schema['paths'].update(schema_2['paths'])
    merged_schema['components']['schemas'].update(schema_2['components']['schemas'])

    with open('openapi/toyaml.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(merged_schema, file, sort_keys=False)

    return merged_schema
